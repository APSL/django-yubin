from celery import shared_task


@shared_task()
def send_email(message_pk):
    """
    Send an email from a database Message PK.
    """
    from .engine import send_db_message
    return send_db_message(message_pk)


@shared_task()
def retry_emails(max_retries=3):
    """
    Retry sending retryable emails enqueueing them again.
    """
    from .models import Message
    enqueued, failed = Message.retry_messages(max_retries)
    return enqueued, failed
