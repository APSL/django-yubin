#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

import logging
from pkg_resources import get_distribution


version = __version__ = get_distribution('django-yubin').version

logger = logging.getLogger('django_yubin')
logger.setLevel(logging.DEBUG)


def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              priority=None):
    """
    Add a new message to the mail queue.

    This is a replacement for Django's ``send_mail`` core email method.

    The `fail_silently``, ``auth_user`` and ``auth_password`` arguments are
    only provided to match the signature of the emulated function. These
    arguments are not used.

    """
    from django.core.mail import EmailMessage
    from django.utils.encoding import force_unicode

    subject = force_unicode(subject)
    email_message = EmailMessage(subject, message, from_email,
                                 recipient_list)
    queue_email_message(email_message, priority=priority)


def mail_admins(subject, message, fail_silently=False, priority=None):
    """
    Add one or more new messages to the mail queue addressed to the site
    administrators (defined in ``settings.ADMINS``).

    This is a replacement for Django's ``mail_admins`` core email method.

    The ``fail_silently`` argument is only provided to match the signature of
    the emulated function. This argument is not used.

    """
    from django.conf import settings as django_settings
    from django.utils.encoding import force_unicode
    from django_yubin import settings

    if priority is None:
        settings.MAIL_ADMINS_PRIORITY

    subject = django_settings.EMAIL_SUBJECT_PREFIX + force_unicode(subject)
    from_email = django_settings.SERVER_EMAIL
    recipient_list = [recipient[1] for recipient in django_settings.ADMINS]
    send_mail(subject, message, from_email, recipient_list, priority=priority)


def mail_managers(subject, message, fail_silently=False, priority=None):
    """
    Add one or more new messages to the mail queue addressed to the site
    managers (defined in ``settings.MANAGERS``).

    This is a replacement for Django's ``mail_managers`` core email method.

    The ``fail_silently`` argument is only provided to match the signature of
    the emulated function. This argument is not used.

    """
    from django.conf import settings as django_settings
    from django.utils.encoding import force_unicode
    from django_yubin import settings

    if priority is None:
        priority = settings.MAIL_MANAGERS_PRIORITY

    subject = django_settings.EMAIL_SUBJECT_PREFIX + force_unicode(subject)
    from_email = django_settings.SERVER_EMAIL
    recipient_list = [recipient[1] for recipient in django_settings.MANAGERS]
    send_mail(subject, message, from_email, recipient_list, priority=priority)


def queue_email_message(email_message, fail_silently=False, priority=None):
    """
    Add new messages to the email queue.

    The ``email_message`` argument should be an instance of Django's core mail
    ``EmailMessage`` class.

    The messages can be assigned a priority in the queue by using the
    ``priority`` argument.

    The ``fail_silently`` argument is not used and is only provided to match
    the signature of the ``EmailMessage.send`` function which it may emulate
    (see ``queue_django_mail``).

    """
    from django_yubin import constants, models, settings

    if constants.PRIORITY_HEADER in email_message.extra_headers:
        priority = email_message.extra_headers.pop(constants.PRIORITY_HEADER)
        priority = constants.PRIORITIES.get(priority.lower())

    if priority == constants.PRIORITY_EMAIL_NOW:
        if constants.EMAIL_BACKEND_SUPPORT:
            from django.core.mail import get_connection
            from django_yubin.engine import send_message
            connection = get_connection(backend=settings.USE_BACKEND)
            result = send_message(email_message, smtp_connection=connection)
            return (result == constants.RESULT_SENT)
        else:
            return email_message.send()
    count = 0
    for to_email in email_message.recipients():
        message = models.Message.objects.create(
            to_address=to_email, from_address=email_message.from_email,
            subject=email_message.subject,
            encoded_message=email_message.message().as_string())
        queued_message = models.QueuedMessage(message=message)
        if priority:
            queued_message.priority = priority
        queued_message.save()
        count += 1
    return count


def queue_django_mail():
    """
    Monkey-patch the ``send`` method of Django's ``EmailMessage`` to just queue
    the message rather than actually send it.

    This method is only useful for Django versions < 1.2.

    """
    from django.core.mail import EmailMessage

    if EmailMessage.send == queue_email_message:
        return False
    EmailMessage._actual_send = EmailMessage.send
    EmailMessage.send = queue_email_message
    EmailMessage.send
    return True


def restore_django_mail():
    """
    Restore the original ``send`` method of Django's ``EmailMessage`` if it has
    been monkey-patched (otherwise, no action is taken).

    This method is only useful for Django versions < 1.2.

    """
    from django.core.mail import EmailMessage

    actual_send = getattr(EmailMessage, '_actual_send', None)
    if not actual_send:
        return False
    EmailMessage.send = actual_send
    del EmailMessage._actual_send
    return True
