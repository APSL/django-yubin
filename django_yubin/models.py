import datetime
import logging
import email
from email import policy
from email import encoders as Encoders
from email.mime.base import MIMEBase
from functools import partial

from django.core.exceptions import FieldError
from django.core.mail.message import (
        ADDRESS_HEADERS,
        EmailMessage,
        EmailMultiAlternatives,
    )
from django.db import models, transaction
from django.db.models import F
from django.utils.module_loading import import_string
from django.utils.text import Truncator
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from mailparser import MailParser

from . import mailparser_utils, tasks


logger = logging.getLogger(__name__)


PARSED_HEADERS_TO_IGNORE = ADDRESS_HEADERS.union({"content-type", "subject", "mime-version"})


class MessageQuerySet(models.QuerySet):
    def retryable(self, max_retries=0):
        qs = self.filter(status__gte=self.model.STATUS_FAILED)
        if max_retries > 0:
            qs = qs.filter(enqueued_count__lt=max_retries)
        return qs


class MessageManager(models.Manager):
    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def retryable(self, max_retries=0):
        return self.get_queryset().retryable(max_retries=max_retries)


class Message(models.Model):
    """
    An email message.
    """
    STATUS_CREATED = 0
    STATUS_QUEUED = 1
    STATUS_IN_PROCESS = 2
    STATUS_SENT = 3
    STATUS_FAILED = 4
    STATUS_BLACKLISTED = 5
    STATUS_DISCARDED = 6
    STATUS_CHOICES = (
        (STATUS_CREATED, _('Created')),
        (STATUS_QUEUED, _('Queued')),
        (STATUS_IN_PROCESS, _('In process')),
        (STATUS_SENT, _('Sent')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_BLACKLISTED, _('Blacklisted')),
        (STATUS_DISCARDED, _('Discarded')),
    )

    to_address = models.TextField(_('to addresses'))
    cc_address = models.TextField(_('cc addresses'), blank=True, default="")
    bcc_address = models.TextField(_('bcc addresses'), blank=True, default="")

    # These fields are to easy access, filtering and searching without parsing the email.
    from_address = models.CharField(_('from address'), max_length=200)
    subject = models.CharField(_('subject'), max_length=255)

    # This field is for internal use in storage backends. They can use it to save the email
    # like the DatabaseSorageBackend, the file path like the FileStorageBackend, etc.
    # Other users must access this data through the ``message_data`` property.
    _message_data = models.TextField(_('message data'), db_column='message_data')

    @property
    def message_data(self):
        storage_backend = import_string(self.storage)
        return storage_backend.get_message_data(self)

    @message_data.setter
    def message_data(self, data):
        storage_backend = import_string(self.storage)
        storage_backend.set_message_data(self, data)

    storage = models.CharField(_('storage backend'), max_length=200, blank=False,
                               default="django_yubin.storage_backends.DatabaseStorageBackend")

    date_created = models.DateTimeField(_('date created'), auto_now_add=True)
    date_sent = models.DateTimeField(_('date sent'), null=True, blank=True)
    sent_count = models.PositiveSmallIntegerField(_('sent count'), default=0,
                                                  help_text=_('Times the message has been sent'))
    date_enqueued = models.DateTimeField(_('date enqueued'), null=True, blank=True)
    enqueued_count = models.PositiveSmallIntegerField(_('enqueued count'), default=0,
                                                      help_text=_('Times the message has been enqueued'))
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_CREATED)

    objects = MessageManager()

    class Meta:
        ordering = ('date_created',)
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __init__(self, *args, **kwargs):
        if '_message_data' in kwargs:
            raise FieldError("_message_data can not be used for creating instances, use message_data.")
        return super().__init__(*args, **kwargs)

    def __str__(self):
        recipients = self.to_address
        if self.cc_address:
            recipients += ', %s' % self.cc_address
        if self.bcc_address:
            recipients += ', %s' % self.bcc_address
        return '%s: %s' % (recipients, self.subject)

    def to(self):
        return [email.strip() for email in self.to_address.split(",") if email.strip()]

    def cc(self):
        return [email.strip() for email in self.cc_address.split(",") if email.strip()]

    def bcc(self):
        return [email.strip() for email in self.bcc_address.split(",") if email.strip()]

    def recipients(self):
        return self.to() + self.cc() + self.bcc()

    def get_message_parser(self):
        message = email.message_from_string(self.message_data, policy=policy.default)
        return MailParser(message)

    def get_email_message(self):
        """
        Returns EmailMultiAlternatives or EmailMessage depending on whether the email is multipart or not.

        Note that this should reconstruct all the kwargs of EmailMessage/EmailMultiAlternatives
        to not lose information. See Github issue #66 for more information.

        XXX: perhaps an inspect.signature combined with **kwargs approach could validate
        against unexpected django changes?
        """
        msg = self.get_message_parser()
        to = self.to() or mailparser_utils.get_addresses(msg.to)
        cc = self.cc() or mailparser_utils.get_addresses(msg.cc)
        bcc = self.bcc()

        # Process headers, but ignore address headers - these are processed explicitly.
        headers = {
            header: value
            for header, value in msg.headers.items()
            if header.lower() not in PARSED_HEADERS_TO_IGNORE
        }

        Email = EmailMultiAlternatives if msg.text_html else EmailMessage
        email = Email(
            subject=msg.subject,
            body='\n'.join(msg.text_plain),
            from_email=mailparser_utils.get_address(msg.from_),
            to=to,
            bcc=bcc,
            headers=headers,
            cc=cc,
            reply_to=mailparser_utils.get_addresses(msg.reply_to),
        )

        # set the multipart subtype
        content_type = msg.headers["Content-Type"].split(";", 1)[0]  # discard boundary
        main_type, subtype = content_type.split("/", 1)
        if main_type == "multipart":
            email.mixed_subtype = subtype

        # NOTE - mailparser only supports text and HTML, any other content types are
        # considered not_managed.
        if msg.text_html:
            email.attach_alternative('<br>'.join(msg.text_html), mimetype='text/html')

        # attachment is a dict with fixed keys:
        # filename, payload, binary, mail_content_type, content-id, content-disposition,
        # charset and content_transfer_encoding
        #
        # This performs generic handling of attachments, respecting the original various
        # ways the attachment can be used.
        for attachment in msg.attachments:
            basetype, subtype = attachment["mail_content_type"].split("/", 1)
            binary = attachment["binary"]
            content = attachment['payload']
            transfer_encoding = attachment["content_transfer_encoding"]

            mime_attachment = MIMEBase(basetype, subtype)
            mime_attachment.set_payload(content)
            if not binary:
                Encoders.encode_base64(mime_attachment)
            else:
                mime_attachment.add_header("Content-Transfer-Encoding", transfer_encoding)
            for header in ("Content-ID", "Content-Disposition"):
                value = attachment[header.lower()]
                if value:
                    mime_attachment.add_header(header, value)
            email.attach(mime_attachment)

        return email

    def add_log(self, log_message):
        Log.objects.create(message=self, action=self.status, log_message=log_message)

    def mark_as(self, status, log_message=None):
        should_refresh_from_db = False

        self.status = status
        if status is self.STATUS_SENT:
            self.date_sent = now()
            self.sent_count = F('sent_count') + 1
            should_refresh_from_db = True
        elif status is self.STATUS_QUEUED:
            self.date_enqueued = now()
            self.enqueued_count = F('enqueued_count') + 1
            should_refresh_from_db = True
        self.save()

        if should_refresh_from_db:
            self.refresh_from_db()

        if log_message is not None:
            self.add_log(log_message)

    def can_be_enqueued(self):
        return self.status in (
            self.STATUS_CREATED,
            self.STATUS_FAILED,
            self.STATUS_BLACKLISTED,
            self.STATUS_DISCARDED
        )

    def enqueue(self, log_message=None):
        """
        Sends the task to enqueue the message on commit.
        """
        if not self.can_be_enqueued():
            self.add_log("Message can not be enqueued in it's current status")
            return False

        transaction.on_commit(partial(tasks.send_email.delay, message_pk=self.pk, log_message=log_message))
        return True

    @classmethod
    def retry_messages(cls, max_retries=3):
        enqueued = 0
        messages = cls.objects.retryable(max_retries)
        for message in messages:
            enqueued += message.enqueue('Retry sending the email.')
        failed = len(messages) - enqueued
        return enqueued, failed

    @classmethod
    def delete_old(cls, days=90):
        """
        Deletes mails created before `days` days.

        Returns the deletion data from Django and the cuttoff date.
        """
        cutoff_date = now() - datetime.timedelta(days)
        deleted = cls.objects.filter(date_created__lt=cutoff_date).delete()
        return deleted, cutoff_date


class Blacklist(models.Model):
    """
    A blacklisted email address.

    Messages attempted to be sent to e-mail addresses which appear on this
    blacklist will be skipped entirely.
    """
    email = models.EmailField(_('email'), max_length=200)
    date_added = models.DateTimeField(_('date added'), default=now)

    class Meta:
        ordering = ('-date_added',)
        verbose_name = _('blacklisted email')
        verbose_name_plural = _('blacklisted emails')

    def __str__(self):
        return self.email


class Log(models.Model):
    """
    A log used to record the activity of a queued message.
    """
    message = models.ForeignKey(Message, verbose_name=_('message'), editable=False, on_delete=models.CASCADE)
    action = models.PositiveSmallIntegerField(_('action'), choices=Message.STATUS_CHOICES,
                                              default=Message.STATUS_CREATED)
    date = models.DateTimeField(_('date'), auto_now_add=True)
    log_message = models.TextField(_('log'), blank=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = _('log')
        verbose_name_plural = _('logs')

    def __str__(self):
        return Truncator(self.log_message).chars(50)
