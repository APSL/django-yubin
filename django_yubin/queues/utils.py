#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------


import logging

from django_yubin import constants, settings
from django_yubin.models import Blacklist, QueuedMessage
from django_yubin.engine import send_queued_message


logger = logging.getLogger('django_yubin.engine')

if constants.EMAIL_BACKEND_SUPPORT:
    from django.core.mail import get_connection
else:
    from django.core.mail import SMTPConnection as get_connection
    logger.warn('DEPRECATION WARNING. Support for Django<1.3 would be removed')


def send_msg_or_internal_enqueue(msg, priority):
    """Enqueue msg at QueuedMessage model and try to send it"""

    # Enqueuing...
    queued_message = QueuedMessage(message=msg)
    if priority:
        queued_message.priority = priority
    queued_message.save()

    try:
        if constants.EMAIL_BACKEND_SUPPORT:
            connection = get_connection(backend=settings.USE_BACKEND)
        else:
            connection = get_connection()

        blacklist = Blacklist.objects.values_list('email', flat=True)
        connection.open()

        result = send_queued_message(
            queued_message,
            smtp_connection=connection,
            blacklist=blacklist)

        logger.debug("Result of sent: {}".format(result))

        connection.close()
    finally:
        logger.debug("Email sending error")