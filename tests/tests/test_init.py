import unittest

from django.conf import settings as django_settings
from django.core import mail

from django_yubin import models, settings, queue_email_message, mail_admins, mail_managers
from django_yubin.models import Message

from .base import MailerTestCase


class TestInit(MailerTestCase):
    """
    Yubin tests for __init__.py.
    """

    @unittest.mock.patch('django_yubin.models.Message.enqueue')
    def testQueueEmailMessage(self, enqueue_email_mock):
        email = mail.EmailMessage(subject='subject', body='body', from_email='mail_from@abc.com',
                                  to=['mail_to@abc.com'])
        queued = queue_email_message(email)
        self.assertEqual(queued, 1)
        self.assertTrue(Message.objects.filter(from_address='mail_from@abc.com').exists())
        self.assertEqual(enqueue_email_mock.call_count, queued)

    @unittest.skip("TODO: Reimplement")
    def testSendMessageTestMode(self):
        # Test mode activated
        settings.MAILER_TEST_MODE = True
        settings.MAILER_TEST_EMAIL = 'test_email@abc.com'
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'])
        msg.send()

        queued_messages = models.QueuedMessage.objects.all()

        self.assertEqual('test_email@abc.com', queued_messages[0].message.to_address)
        self.assertTrue('test_email@abc.com' in queued_messages[0].message.encoded_message)
        self.assertTrue('X-Yubin-Test-Original: mail_to@abc.com' in
                        queued_messages[0].message.encoded_message)

    @unittest.skip("TODO: Reimplement")
    def testSendMessageAdminTestMode(self):
        # Test mode activated sending mail to admins
        settings.MAILER_TEST_MODE = True
        settings.MAILER_TEST_EMAIL = 'test_email@abc.com'
        mail_admins(subject='subject', message='message')

        queued_messages = models.QueuedMessage.objects.all()
        recipient_list = [recipient[1] for recipient in django_settings.ADMINS]

        self.assertEqual('test_email@abc.com', queued_messages[0].message.to_address)
        self.assertTrue('test_email@abc.com' in queued_messages[0].message.encoded_message)
        self.assertTrue('X-Yubin-Test-Original: {}'.format(','.join(recipient_list)) in
                        queued_messages[0].message.encoded_message)

    @unittest.skip("TODO: Reimplement")
    def testSendMessageManagersTestMode(self):
        # Test mode activated sending mail to admins
        settings.MAILER_TEST_MODE = True
        settings.MAILER_TEST_EMAIL = 'test_email@abc.com'
        mail_managers(subject='subject', message='message')

        queued_messages = models.QueuedMessage.objects.all()
        recipient_list = [recipient[1] for recipient in django_settings.MANAGERS]

        self.assertEqual('test_email@abc.com', queued_messages[0].message.to_address)
        self.assertTrue('test_email@abc.com' in queued_messages[0].message.encoded_message)
        self.assertTrue('X-Yubin-Test-Original: {}'.format(','.join(recipient_list)) in
                        queued_messages[0].message.encoded_message)
