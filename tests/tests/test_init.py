from unittest.mock import patch

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.test import TestCase

from django_yubin import settings, queue_email_message, send_mail, mail_admins, mail_managers
from django_yubin.models import Message


@patch('django_yubin.models.Message.enqueue')
class TestInit(TestCase):
    """
    Yubin tests for __init__.py.
    """

    def test_queue_email_message(self, enqueue_email_mock):
        email = EmailMessage(subject='subject', body='body', from_email='mail_from@abc.com',
                             to=['mail_to@abc.com'])
        queued = queue_email_message(email)
        self.assertEqual(queued, 1)
        self.assertEqual(enqueue_email_mock.call_count, queued)
        self.assertTrue(Message.objects.filter(from_address='mail_from@abc.com').exists())

    def test_queue_email_message_test_mode(self, enqueue_email_mock):
        settings.MAILER_TEST_MODE = True
        settings.MAILER_TEST_EMAIL = 'test_email@abc.com'

        to = ['mail_to@abc.com']
        email = EmailMessage(subject='subject', body='body', from_email='mail_from@abc.com', to=to)
        queued = queue_email_message(email)
        self.assertEqual(queued, 1)
        self.assertEqual(enqueue_email_mock.call_count, queued)

        messages = Message.objects.all()
        self.assertEqual(len(messages), 1)

        self.assertEqual(settings.MAILER_TEST_EMAIL, messages[0].to_address)
        self.assertTrue(settings.MAILER_TEST_EMAIL in messages[0].encoded_message)
        self.assertTrue('X-Yubin-Test-Original: %s' % to[0] in messages[0].encoded_message)

        settings.MAILER_TEST_MODE = False

    def test_send_mail(self, enqueue_email_mock):
        recipient_list = ['mail_to@abc.com']
        send_mail(subject='subject', message='body', from_email='mail_from@abc.com',
                  recipient_list=recipient_list)
        self.assertEqual(enqueue_email_mock.call_count, 1)

        messages = Message.objects.all()
        self.assertEqual(len(messages), 1)

        self.assertEqual(recipient_list[0], messages[0].to_address)
        self.assertTrue(recipient_list[0] in messages[0].encoded_message)

    def test_send_message_admin(self, enqueue_email_mock):
        mail_admins(subject='subject', message='message')

        messages = Message.objects.all()
        recipient_list = [recipient[1] for recipient in django_settings.ADMINS]
        self.assertEqual(len(messages), len(recipient_list))
        self.assertEqual(enqueue_email_mock.call_count, len(recipient_list))

        for i, recipient in enumerate(recipient_list):
            self.assertEqual(recipient, messages[i].to_address)
            self.assertTrue(recipient in messages[i].encoded_message)

    def test_send_message_managers(self, enqueue_email_mock):
        mail_managers(subject='subject', message='message')

        messages = Message.objects.all()
        messages = Message.objects.all()
        recipient_list = [recipient[1] for recipient in django_settings.MANAGERS]
        self.assertEqual(len(messages), len(recipient_list))
        self.assertEqual(enqueue_email_mock.call_count, len(recipient_list))

        for i, recipient in enumerate(recipient_list):
            self.assertEqual(recipient, messages[i].to_address)
            self.assertTrue(recipient in messages[i].encoded_message)
