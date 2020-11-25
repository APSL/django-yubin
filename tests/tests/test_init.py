import unittest

from django.conf import settings as django_settings
from django.core import mail
from django.utils.encoding import force_text

from django_yubin import models, constants, settings, mail_admins, mail_managers

from .base import MailerTestCase


@unittest.skip("TODO: Reimplement")
class TestInit(MailerTestCase):
    """
    Yubin tests for __init__.py.

    WARN: Copied from old test_backend.py
    TODO: Reimplement all the tests.
    """

    def testUnicodeErrorQueuedMessage(self):
        """
        Checks that we capture unicode errors on mail
        """
        from django.core.management import call_command
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email=u'juan.lópez@abc.com', to=['mail_to@abc.com'])
        msg.send()
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 1)
        call_command('send_mail', verbosity='0')
        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 1)

    def testUnicodeQueuedMessage(self):
        """
        Checks that we capture unicode errors on mail
        """
        from django.core.management import call_command
        msg = mail.EmailMessage(subject=u'Chère maman',
                                body='Je t\'aime très fort',
                                from_email='mail_from@abc.com',
                                to=['to@example.com'])
        msg.send()

        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 1)

        call_command('send_mail', verbosity='0')

        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 0)

        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 0)

        message = msg.message()
        self.assertEqual(message['subject'], '=?utf-8?q?Ch=C3=A8re_maman?=')
        self.assertEqual(force_text(message.get_payload()), 'Je t\'aime très fort')

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
