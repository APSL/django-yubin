"""
The "engine room" of django-yubin mailer.

Functions here actually handle the sending of messages.
"""

import logging

from django.core.mail import get_connection
from django.db import transaction

from . import models, settings


logger = logging.getLogger(__name__)


@transaction.atomic
def send_db_message(message_pk):
    """
    Sends a django_yubin.models.Message by its PK.
    """
    try:
        # Lock the message
        message = models.Message.objects.select_for_update().get(pk=message_pk)
    except Exception:
        msg = 'Could not fetch and lock the message from the database'
        logger.exception(msg, extra={'message_pk': message_pk})
        return False

    if message.status != models.Message.STATUS_QUEUED:
        msg = "Message is not in queue status, ignoring the email."
        logger.warning(msg)
        message.add_log(msg)
        return False

    message.mark_as(models.Message.STATUS_IN_PROCESS, "Trying to send the message.")

    if models.Blacklist.objects.filter(email=message.to_address).exists():
        msg = "Not sending to blacklisted email: %s" % message.to_address
        logger.info(msg)
        message.mark_as(models.Message.STATUS_BLACKLISTED, msg)
        return False

    if settings.PAUSE_SEND:
        msg = "Sending is paused, discarding the email."
        logger.info(msg)
        message.mark_as(models.Message.STATUS_DISCARDED, msg)
        return False

    try:
        connection = get_connection(backend=settings.USE_BACKEND)
        connection.send_messages([message.get_email_message()])
        msg = "Message sent %s" % message
        logger.info(msg)
        message.mark_as(models.Message.STATUS_SENT, msg)
        return True
    except (OSError, ValueError) as e:
        logger.exception("Message sending has failed", extra={'email_message': message})
        message.mark_as(models.Message.STATUS_FAILED, str(e))
        return False
