import logging

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def send_email(message_pk):
    """
    Send an email from a database Message PK.
    """
    from .models import Message
    from . import engine

    try:
        message = Message.objects.get(pk=message_pk)
    except Exception:
        msg = 'Could not fetch the message from the database'
        logger.exception(msg, extra={'message_pk': message_pk})
        return

    try:
        engine.send_db_message(message)
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
        send_email.signature().delay(message.pk)
        message.mark_as_queued()
        message.save()

    logger.info('%s messages have been queued again.' % len(messages))
