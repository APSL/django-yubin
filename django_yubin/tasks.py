import logging

from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_email(self, message_pk):
    from django.core.mail import get_connection
    from django_yubin import settings
    from django_yubin.engine import send_message
    from django_yubin.models import Message

    try:
        message = Message.objects.get(pk=message_pk)
        # TODO: email_message = message.??
    except Exception:
        logger.exception('Could not fetch the message from the database',
                         extra={'message_pk': message_pk})
        return

    # connection = get_connection(backend=settings.USE_BACKEND)
    # result = send_message(email_message, smtp_connection=connection)
    # return result == constants.RESULT_SENT
