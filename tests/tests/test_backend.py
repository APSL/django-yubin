# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from unittest import skipIf

from django.conf import settings as django_settings
from django.core import mail
from django.core.management import call_command
from django.utils.encoding import force_text

from django_yubin import models, constants, settings, mail_admins, mail_managers

from .base import MailerTestCase, RFC_6532_SUPPORT


class TestBackend(MailerTestCase):
    """
    Backend tests for the django_yubin app.
    """

    def setUp(self):
        super(TestBackend, self).setUp()
        if hasattr(django_settings, 'EMAIL_BACKEND'):
            self.old_email_backend = django_settings.EMAIL_BACKEND
        else:
            self.old_email_backend = None
        django_settings.EMAIL_BACKEND = 'django_yubin.smtp_queue.'\
                                        'EmailBackend'

    def tearDown(self):
        super(TestBackend, self).tearDown()
        if self.old_email_backend:
            django_settings.EMAIL_BACKEND = self.old_email_backend
        else:
            delattr(django_settings, 'EMAIL_BACKEND')

    def testQueuedMessagePriorities(self):
        # now_not_queued priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'now-not-queued'})
        msg.send()

        # now priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'now'})
        msg.send()

        # high priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'high'})
        msg.send()

        # low priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'low'})
        msg.send()

        # normal priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'normal'})
        msg.send()

        # normal priority message (no explicit priority header)
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'])
        msg.send()

        qs = models.Message.objects.all()
        self.assertEqual(qs.count(), 5)

        qs = models.QueuedMessage.objects.all()
        self.assertEqual(qs.count(), 4)

        qs = models.QueuedMessage.objects.now_priority()
        self.assertEqual(qs.count(), 0)

        qs = models.QueuedMessage.objects.high_priority()
        self.assertEqual(qs.count(), 1)
        queued_message = qs[0]
        self.assertEqual(queued_message.priority, constants.PRIORITY_HIGH)

        qs = models.QueuedMessage.objects.low_priority()
        self.assertEqual(qs.count(), 1)
        queued_message = qs[0]
        self.assertEqual(queued_message.priority, constants.PRIORITY_LOW)

        qs = models.QueuedMessage.objects.normal_priority()
        self.assertEqual(qs.count(), 2)
        for queued_message in qs:
            self.assertEqual(queued_message.priority,
                             constants.PRIORITY_NORMAL)

    @skipIf(not RFC_6532_SUPPORT, 'RFC 6532 not supported')
    def testUnicodeErrorQueuedMessage(self):
        """
        Checks that we capture unicode errors on mail
        """
        from django.core.management import call_command
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email=u'juan.lópez@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'normal'})
        msg.send()
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 1)
        call_command('send_mail', verbosity='0')
        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 1)

    @skipIf(not RFC_6532_SUPPORT, 'RFC 6532 not supported')
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

    @skipIf(not RFC_6532_SUPPORT, 'RFC 6532 not supported')
    def testUnicodePriorityNowNotQueuedMessage(self):
        """
        Checks that we capture unicode errors on mail on priority.
        It's hard to check as by definiton priority email does not Logs its
        contents.
        """
        msg = mail.EmailMessage(subject=u'Chère maman',
                                body='Je t\'aime très fort',
                                from_email='mail_from@abc.com',
                                to=['to@example.com'],
                                headers={'X-Mail-Queue-Priority': 'now-not-queued'})
        num_sent = mail.get_connection().send_messages([msg])
        self.assertEqual(num_sent, 1)
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 0)
        call_command('send_mail', verbosity='0')
        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 0)
        message = msg.message()
        self.assertEqual(message['subject'], '=?utf-8?q?Ch=C3=A8re_maman?=')
        self.assertEqual(force_text(message.get_payload()), 'Je t\'aime très fort')

    def testSendMessageNowPriority(self):
        # NOW priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'now'})
        msg.send()

        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 0)

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

    def testHighPriority(self):
        self.assertEqual(models.QueuedMessage.objects.all().count(), 0)
        self.assertEqual(models.Message.objects.all().count(), 0)
        self.assertEqual(models.Log.objects.all().count(), 0)

        # Test with default priority
        msg = mail.EmailMessage(subject='subject 1', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'])
        msg.send()

        self.assertEqual(models.Message.objects.all().count(), 1)
        self.assertEqual(models.QueuedMessage.objects.all().count(), 1)
        self.assertEqual(models.Log.objects.all().count(), 0)

        # Test with high priority
        msg = mail.EmailMessage(subject='subject 2', body='body',
                                from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                                headers={'X-Mail-Queue-Priority': 'now'})
        msg.send()

        self.assertEqual(models.QueuedMessage.objects.all().count(), 1)
        self.assertEqual(models.Message.objects.all().count(), 2)
        self.assertEqual(models.Log.objects.all().count(), 1)
