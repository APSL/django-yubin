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


def send_db_message(message, connection=None, blacklist=None, log=True):
    """
    Sends a django_yubin.models.Message.

    To allow optimizations when multiple messages are going to be sent, an SMTP
    connection can be provided and a list of blacklisted email addresses.
    Otherwise an SMTP connection will be opened to send this message and the
    email recipient address checked against the ``Blacklist`` table.

    If the message recipient is blacklisted, the message will be removed from
    the queue without being sent. Otherwise, the message is attempted to be
    sent with an SMTP failure resulting in the message being flagged as
    deferred so it can be tried again later.

    By default, a log is created as to the action. Either way, the original
    message is not deleted.
    """
    message.status = models.Message.STATUS_IN_PROCESS
    message.save()

    log_message = ''

    if connection is None:
        connection = get_connection(backend=settings.USE_BACKEND)
    opened_connection = False

    if blacklist is None:
        blacklisted = models.Blacklist.objects.filter(email=message.to_address)
    else:
        blacklisted = message.to_address in blacklist

    if blacklisted:
        msg = "Not sending to blacklisted email: %s" % message.to_address.encode("utf-8")
        logger.info(msg)
        log_message = msg
        message.status = models.Message.STATUS_BLACKLISTED
    elif settings.PAUSE_SEND:
        msg = "Sending is paused, discarding the email."
        logger.info(msg)
        log_message = msg
        message.status = models.Message.STATUS_DISCARDED
    else:
        try:
            logger.info("Sending message to %s: %s" %
                        (message.to_address.encode("utf-8"),
                         message.subject.encode("utf-8")))
            opened_connection = connection.open()
            connection.send_messages([message])
            message.mark_as_sent()
        except (SocketError,
                smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError,
                UnicodeDecodeError, UnicodeEncodeError) as e:
            logger.exception("Message sending has failed", extra={'message': message})
            try:
                log_message = unicode(e)
            except NameError:
                log_message = e
            message.status = models.Message.STATUS_FAILED

    message.save()

    if log:
        models.Log.objects.create(message=message, action=message.status, log_message=log_message)

    if opened_connection:
        connection.close()
