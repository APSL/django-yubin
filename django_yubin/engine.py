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
def send_db_message(message_pk, log_message=None):
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

    # Messages in STATUS_QUEUED can be sent to keep compatibility with previous yubin version.
    # In future versions that condition can be removed and only check `can_be_enqueued()`.
    if message.status != models.Message.STATUS_QUEUED:
        if not message.can_be_enqueued():
            msg = "Message can not be enqueued in it's current status."
            logger.warning(msg)
            message.add_log(msg)
            return False

    message.mark_as(models.Message.STATUS_QUEUED, log_message)
    message.mark_as(models.Message.STATUS_IN_PROCESS, "Trying to send the message.")

    recipients = message.recipients()
    if models.Blacklist.objects.filter(email__in=recipients).exists():
        msg = "Not sending due blacklisted email in: %s" % recipients
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
    except Exception as e:
        logger.exception("Message sending has failed", extra={'email_message': message})
        message.mark_as(models.Message.STATUS_FAILED, str(e))
        return False
