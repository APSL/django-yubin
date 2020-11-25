from django.core import mail
from django.test import TestCase

from django_yubin import queue_email_message


class MailerTestCase(TestCase):
    """
    Base class for Django Mailer test cases.
    """

    def queue_message(self, subject='test', message='a test message',
                      from_email='sender@djangoyubin.com',
                      recipient_list=('recipient@djangomailer',)):
        """
        Easy way to queue a simple message.
        """
        email_message = mail.EmailMessage(subject, message, from_email, recipient_list)
        return queue_email_message(email_message)
