from django.core.mail import EmailMessage

from django_yubin.models import Message


class MessageMixin:
    @staticmethod
    def create_message(
        subject="Lorem ipsum dolor sit amet",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        from_address="no-reply@acmecorp.com",
        to_address="johndoe@acmecorp.com",
        status=Message.STATUS_CREATED,
    ):
        email = EmailMessage(subject, body, to=[to_address], from_email=from_address)
        return Message.objects.create(
            to_address=email.to[0],
            from_address=email.from_email,
            subject=email.subject,
            encoded_message=email.message().as_string(),
            status=status,
        )
