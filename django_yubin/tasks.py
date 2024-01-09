from celery import shared_task


@shared_task()
def send_email(message_pk, log_message=None):
    """
    Send an email from a database Message PK.
    """
    from .engine import send_db_message
    return send_db_message(message_pk, log_message)


@shared_task()
def retry_emails(max_retries=3):
    """
    Retry sending retryable emails enqueueing them again.
    """
    from .models import Message
    enqueued, failed = Message.retry_messages(max_retries)
    return enqueued, failed


@shared_task()
def delete_old_emails(days=90):
    """
    Delete emails created before `days` days (default 90).
    """
    from .models import Message
    deleted, cutoff_date = Message.delete_old(days)
    return deleted, cutoff_date
