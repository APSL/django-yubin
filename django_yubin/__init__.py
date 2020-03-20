import logging

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.utils.encoding import force_text

from django_yubin import models, settings
from django_yubin.tasks import send_email


logger = logging.getLogger('django_yubin')


def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None):
    """
    Add a new message to the mail queue.

    This is a replacement for Django's ``send_mail`` core email method.

    The `fail_silently``, ``auth_user`` and ``auth_password`` arguments are
    only provided to match the signature of the emulated function. These
    arguments are not used.
    """
    subject = force_text(subject)
    email_message = EmailMessage(subject, message, from_email, recipient_list)
    queue_email_message(email_message)


def mail_admins(subject, message, fail_silently=False):
    """
    Add one or more new messages to the mail queue addressed to the site
    administrators (defined in ``settings.ADMINS``).

    This is a replacement for Django's ``mail_admins`` core email method.

    The ``fail_silently`` argument is only provided to match the signature of
    the emulated function. This argument is not used.
    """
    subject = django_settings.EMAIL_SUBJECT_PREFIX + force_text(subject)
    from_email = django_settings.SERVER_EMAIL
    recipient_list = [recipient[1] for recipient in django_settings.ADMINS]
    send_mail(subject, message, from_email, recipient_list)


def mail_managers(subject, message, fail_silently=False):
    """
    Add one or more new messages to the mail queue addressed to the site
    managers (defined in ``settings.MANAGERS``).

    This is a replacement for Django's ``mail_managers`` core email method.

    The ``fail_silently`` argument is only provided to match the signature of
    the emulated function. This argument is not used.
    """
    subject = django_settings.EMAIL_SUBJECT_PREFIX + force_text(subject)
    from_email = django_settings.SERVER_EMAIL
    recipient_list = [recipient[1] for recipient in django_settings.MANAGERS]
    send_mail(subject, message, from_email, recipient_list)


def queue_email_message(email_message, fail_silently=False):
    """
    Add new messages to the email queue.

    The ``email_message`` argument should be an instance of Django's core mail
    ``EmailMessage`` class.

    The ``fail_silently`` argument is not used and is only provided to match
    the signature of the ``EmailMessage.send`` function which it may emulate
    (see ``queue_django_mail``).
    """
    if settings.MAILER_TEST_MODE and settings.MAILER_TEST_EMAIL:
        email_message = set_message_test_mode(email_message, settings.MAILER_TEST_EMAIL)

    count = 0
    for to_email in email_message.recipients():
        message = models.Message.objects.create(
            to_address=to_email,
            from_address=email_message.from_email,
            subject=email_message.subject,
            encoded_message=email_message.message().as_string())
        send_email.delay(message.pk)
        count += 1
    return count


def set_message_test_mode(email_message, mailer_test_email):
    """
    Sets the headers of the message with test values used when
    ``MAILER_TEST_MODE`` setting is ``True``
    """
    original_to = ','.join(email_message.to)
    email_message.extra_headers['X-Yubin-Test-Original'] = original_to
    email_message.to = [mailer_test_email]
    email_message.cc = []
    email_message.bcc = []
    return email_message
