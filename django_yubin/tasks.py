from collections import namedtuple
import logging

from celery import shared_task
from kombu.exceptions import KombuError


logger = logging.getLogger(__name__)


@shared_task()
def send_email(message_pk):
    """
    Send an email from a database Message PK.
    """
    from django.db import transaction
    from .models import Message
    from . import engine

    # Some message-brokers may send messages more than once, we must be
    # idempotent and send emails only once.
    with transaction.atomic():
        try:
            message = Message.objects.select_for_update().get(pk=message_pk)
            # Wait for the lock.
            message.save(update_fields=['date_created'])
            # Update values in case other task has processed the same email.
            message.refresh_from_db()
        except Exception:
            msg = 'Could not fetch the message from the database'
            logger.exception(msg, extra={'message_pk': message_pk})
            return

        try:
            if message.can_be_sent():
                engine.send_db_message(message)
            else:
                logger.info('Message %s can not be sent, skipping it.' % message_pk)
        except Exception:
            logger.exception('Error sending email', extra={'message_pk': message_pk})


EnqueuedFailed = namedtuple('EnqueuedFailed', 'enqueued, failed')


@shared_task()
def retry_emails(max_retries=3):
    """
    Retry sending retryable emails enqueueing them again.
    """
    from .models import Message

    enqueued = 0
    messages = Message.objects.retryable(max_retries)
    for message in messages:
        try:
            message.enqueue('Retry sending the email.')
            enqueued += 1
        except KombuError:
            logger.exception('Error enqueuing again an email', extra={'email_message': message})
    failed = len(messages) - enqueued

    msg = '%s messages have been queued again, %s failed.'
    logger.info(msg % (enqueued, failed))
    return EnqueuedFailed(enqueued, failed)
