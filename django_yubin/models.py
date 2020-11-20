import datetime

from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.db import models
from django.db.models import F
from django.utils.encoding import force_bytes
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from pyzmail.parse import message_from_string, message_from_bytes

from .message_utils import get_attachments, is_part_encoded


class Message(models.Model):
    """
    An email message.

    The ``to_address``, ``from_address`` and ``subject`` fields are merely for
    easy of access for these common values. The ``encoded_message`` field
    contains the entire encoded email message ready to be sent to an SMTP
    connection.
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
    SENDABLE_STATUSES = (STATUS_CREATED, STATUS_FAILED, STATUS_BLACKLISTED, STATUS_DISCARDED)

    to_address = models.CharField(_('to address'), max_length=200)
    from_address = models.CharField(_('from address'), max_length=200)
    subject = models.CharField(_('subject'), max_length=255)

    encoded_message = models.TextField(_('encoded message'))
    date_created = models.DateTimeField(_('date created'), auto_now_add=True)

    date_sent = models.DateTimeField(_('date sent'), null=True, blank=True)
    sent_count = models.PositiveSmallIntegerField(_('sent count'), default=0,
                                                  help_text=_('Times the message has been sent'))

    date_enqueued = models.DateTimeField(_('date enqueued'), null=True, blank=True)
    enqueued_count = models.PositiveSmallIntegerField(_('enqueued count'), default=0,
                                                      help_text=_('Times the message has been enqueued'))

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_CREATED)

    class Meta:
        ordering = ('date_created',)
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return '%s: %s' % (self.to_address, self.subject)

    def can_be_sent(self):
        return self.status not in Message.SENDABLE_STATUSES

    def mark_as_sent(self, log_message=None):
        self.date_sent = now()
        self.status = self.STATUS_SENT
        self.sent_count = F('sent_count') + 1
        self.save()
        if log_message:
            self.add_log(log_message)

    def mark_as_queued(self, log_message=None):
        self.date_enqueued = now()
        self.status = self.STATUS_QUEUED
        self.enqueued_count = F('enqueued_count') + 1
        self.save()
        if log_message:
            self.add_log(log_message)

    def get_pyz_message(self):
        try:
            msg = message_from_string(self.encoded_message)
        except UnicodeEncodeError:
            msg = message_from_string(force_bytes(self.encoded_message))
        except (TypeError, AttributeError):
            msg = message_from_bytes(self.encoded_message)
        return msg

    def get_email_message(self):
        """
        Returns EmailMessage or EmailMultiAlternatives from self, depending on if the
        message has an HTML body.
        """
        msg = self.get_pyz_message()

        body = ''
        if msg.text_part:
            body = msg.text_part.part.get_payload(decode=is_part_encoded(msg, 'text_part'))

        email_class = EmailMessage
        email_kwargs = {
            'subject': msg.get_subject(),
            'body': body,
            'from_email': msg.get_address('from'),
            'to': msg.get_address('to'),
            'cc': msg.get_address('cc'),
            'bcc': msg.get_address('bcc'),
            'attachments': get_attachments(msg),
        }

        html = ''
        if msg.html_part:
            html = msg.html_part.part.get_payload(decode=is_part_encoded(msg, 'html_part'))

        if html:
            email_class = EmailMultiAlternatives
            email_kwargs['alternatives'] = [html]

        return email_class(**email_kwargs)

    def add_log(self, log_message):
        Log.objects.create(message=self, action=self.status, log_message=log_message)

    @classmethod
    def get_not_sent(cls, max_retries=0):
        messages = cls.objects.filter(sent_count=0, status__gt=cls.STATUS_SENT)
        if max_retries > 0:
            messages = messages.filter(enqueued_count__lt=max_retries)
        return messages

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
    date = models.DateTimeField(_('date'), default=now)
    log_message = models.TextField(_('log'), blank=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = _('log')
        verbose_name_plural = _('logs')
