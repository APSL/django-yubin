from django.db import models
from django.utils.encoding import force_bytes
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from pyzmail.parse import message_from_string, message_from_bytes

from . import constants, managers


PRIORITIES = (
    (constants.PRIORITY_NOW, 'now'),
    (constants.PRIORITY_HIGH, 'high'),
    (constants.PRIORITY_NORMAL, 'normal'),
    (constants.PRIORITY_LOW, 'low'),
)

RESULT_CODES = (
    (constants.RESULT_SENT, 'success'),
    (constants.RESULT_SKIPPED, 'not sent (blacklisted or paused)'),
    (constants.RESULT_FAILED, 'failure'),
)


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
        (STATUS_CREATED, _('created')),
        (STATUS_QUEUED, _('queued')),
        (STATUS_IN_PROCESS, _('in process')),
        (STATUS_SENT, _('sent')),
        (STATUS_FAILED, _('failed')),
        (STATUS_BLACKLISTED, _('blacklisted')),
        (STATUS_DISCARDED, _('discarded')),
    )

    to_address = models.CharField(_('to address'), max_length=200)
    from_address = models.CharField(_('from address'), max_length=200)
    subject = models.CharField(_('subject'), max_length=255)

    encoded_message = models.TextField(_('encoded message'))
    date_created = models.DateTimeField(_('date created'), default=now)
    date_sent = models.DateTimeField(_('date sent'), null=True, blank=True)
    sent_count = models.PositiveSmallIntegerField(_('sent count'), default=0,
                                                  help_text=_('Times the message has been sent'))

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_CREATED)

    class Meta:
        ordering = ('date_created',)
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return '%s: %s' % (self.to_address, self.subject)

    def get_pyz_message(self):
        try:
            msg = message_from_string(self.encoded_message)
        except UnicodeEncodeError:
            msg = message_from_string(force_bytes(self.encoded_message))
        except (TypeError, AttributeError):
            msg = message_from_bytes(self.encoded_message)
        return msg


class QueuedMessage(models.Model):
    """
    A queued message.

    Messages in the queue can be prioritised so that the higher priority
    messages are sent first (secondarily sorted by the oldest message).

    WARN: Deprecated. It will be deleted after the migration process is finished.
    """
    message = models.OneToOneField(Message, editable=False, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField(choices=PRIORITIES,
                                                default=constants.PRIORITY_NORMAL)
    deferred = models.DateTimeField(null=True, blank=True)
    retries = models.PositiveIntegerField(default=0)
    date_queued = models.DateTimeField(default=now)

    objects = managers.QueueManager()

    class Meta:
        ordering = ('priority', 'date_queued')

    def defer(self):
        self.deferred = now()
        self.save()


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


class Log(models.Model):
    """
    A log used to record the activity of a queued message.
    """
    message = models.ForeignKey(Message, verbose_name=_('message'), editable=False, on_delete=models.CASCADE)
    result = models.PositiveSmallIntegerField(choices=RESULT_CODES, null=True,
                                              help_text=_('Deprecated for new emails, see "action"'))
    action = models.PositiveSmallIntegerField(_('action'), choices=Message.STATUS_CHOICES,
                                              default=Message.STATUS_CREATED)
    date = models.DateTimeField(_('date'), default=now)
    log_message = models.TextField(_('log'), blank=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = ('log')
        verbose_name_plural = _('logs')
