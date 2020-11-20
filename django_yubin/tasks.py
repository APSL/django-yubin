import logging

from celery import shared_task
from kombu.exceptions import OperationalError


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
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
                logger.info('Message %s already in progress or sent, skipping it.' % message_pk)
        except Exception:
            logger.exception('Error sending email', extra={'message_pk': message_pk})


@shared_task(ignore_result=True)
def retry_not_sent(max_retries=3):
    """
    Retry sending not sent emails queueing them again.
    """
    from .models import Message

    messages = Message.get_not_sent(max_retries)
    for message in messages:
        try:
            send_email.signature().delay(message.pk)
            message.mark_as_queued(log_message='Retry sending the email.')
        except OperationalError:
            logger.exception('Error enqueuing again an email', extra={'message': message})

    logger.info('%s messages have been queued again.' % len(messages))
