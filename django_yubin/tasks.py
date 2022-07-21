from collections import namedtuple
import logging

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task()
def send_email(message_pk):
    """
    Send an email from a database Message PK.
    """
    from .engine import send_db_message
    send_db_message(message_pk)


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
        enqueued += message.enqueue('Retry sending the email.')

    failed = len(messages) - enqueued
    logger.info('%s messages have been queued again, %s failed.' % (enqueued, failed))
    return EnqueuedFailed(enqueued, failed)
