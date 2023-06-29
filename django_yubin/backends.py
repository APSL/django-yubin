"""
Email backends.
"""

from django.core.mail.backends.base import BaseEmailBackend

from django_yubin import queue_email_message


class QueuedEmailBackend(BaseEmailBackend):
    """
    A wrapper that manages a queued SMTP system.
    """

    def send_messages(self, email_messages):
        """
        Add new messages to the email queue.

        The ``email_messages`` argument should be one or more instances
        of Django's core mail ``EmailMessage`` class.
        """
        num_sent = 0
        for email_message in email_messages:
            num_sent += queue_email_message(email_message)
        return num_sent
