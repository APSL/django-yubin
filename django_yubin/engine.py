"""
The "engine room" of django-yubin mailer.

Functions here actually handle the sending of messages.
"""

import logging
import smtplib
from socket import error as SocketError

from django.core.mail import get_connection

from . import models, settings


logger = logging.getLogger(__name__)


def send_db_message(message, blacklist=None, log=True):
    """
    Sends a django_yubin.models.Message.

    If the message recipient is blacklisted, the message will be removed from
    the queue without being sent. Otherwise, the message is attempted to be
    sent with an SMTP failure resulting in the message being flagged as
    deferred so it can be tried again later.

    By default, a log is created as to the action. Either way, the original
    message is not deleted.
    """
    log_message = ''
    message.mark_as(models.Message.STATUS_IN_PROCESS)

    if blacklist:
        blacklisted = message.to_address in blacklist
    else:
        blacklisted = models.Blacklist.objects.filter(email=message.to_address).exists()

    if blacklisted:
        msg = "Not sending to blacklisted email: %s" % message.to_address
        logger.info(msg)
        log_message = msg
        message.mark_as(models.Message.STATUS_BLACKLISTED)
    elif settings.PAUSE_SEND:
        msg = "Sending is paused, discarding the email."
        logger.info(msg)
        log_message = msg
        message.mark_as(models.Message.STATUS_DISCARDED)
    else:
        try:
            logger.info("Sending message to %s: %s" % (message.to_address, message.subject))
            connection = get_connection(backend=settings.USE_BACKEND)
            connection.send_messages([message.get_email_message()])
            message.mark_as(models.Message.STATUS_SENT)
        except (SocketError,
                smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError,
                UnicodeDecodeError, UnicodeEncodeError) as e:
            logger.exception("Message sending has failed", extra={'message': message})
            log_message = str(e)
            message.mark_as(models.Message.STATUS_FAILED)

    if log:
        models.Log.objects.create(message=message, action=message.status, log_message=log_message)
