#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

from unittest import skipIf

from django.conf import settings as django_settings
from django.core import mail

import six
from django_yubin import models, constants, queue_email_message
from .base import MailerTestCase


class TestBackend(MailerTestCase):
    """
    Backend tests for the django_yubin app.

    For Django versions less than 1.2, these tests are still run but they just
    use the queue_email_message funciton rather than directly sending messages.

    """

    def setUp(self):
        super(TestBackend, self).setUp()
        if constants.EMAIL_BACKEND_SUPPORT:
            if hasattr(django_settings, 'EMAIL_BACKEND'):
                self.old_email_backend = django_settings.EMAIL_BACKEND
            else:
                self.old_email_backend = None
            django_settings.EMAIL_BACKEND = 'django_yubin.smtp_queue.'\
                                            'EmailBackend'

    def tearDown(self):
        super(TestBackend, self).tearDown()
        if constants.EMAIL_BACKEND_SUPPORT:
            if self.old_email_backend:
                django_settings.EMAIL_BACKEND = self.old_email_backend
            else:
                delattr(django_settings, 'EMAIL_BACKEND')

    def send_message(self, msg):
        if constants.EMAIL_BACKEND_SUPPORT:
            msg.send()
        else:
            queue_email_message(msg)

    def testQueuedMessagePriorities(self):
        # high priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'high'})
        self.send_message(msg)

        # low priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'low'})
        self.send_message(msg)

        # normal priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'normal'})
        self.send_message(msg)

        # normal priority message (no explicit priority header)
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email='mail_from@abc.com', to=['mail_to@abc.com'])
        self.send_message(msg)

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

    @skipIf(six.PY3, 'RFC 6532 is not properly supported in Django/Py3')
    def testUnicodeQueuedMessage(self):
        """
        Checks that we capture unicode errors on mail
        """
        from django.core.management import call_command
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email=u'juan.lópez@abc.com', to=['mail_to@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'normal'})
        self.send_message(msg)
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 1)
        call_command('send_mail', verbosity='0')
        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 1)

    def testUnicodePriorityMessage(self):
        """
        Checks that we capture unicode errors on mail on priority.
        It's hard to check as by definiton priority email does not Logs its
        contents.
        """
        from django.core.management import call_command
        msg = mail.EmailMessage(subject=u'á subject', body='body',
                        from_email=u'juan.lópez@abc.com', to=[u'únñac@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'now'})
        self.send_message(msg)
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 0)
        call_command('send_mail', verbosity='0')
        num_errors = models.Log.objects.filter(result=constants.RESULT_FAILED).count()
        self.assertEqual(num_errors, 0)

    def testSendMessageNowPriority(self):
        # NOW priority message
        msg = mail.EmailMessage(subject='subject', body='body',
                        from_email='mail_from@abc.com', to=['mail_to@abc.com'],
                        headers={'X-Mail-Queue-Priority': 'now'})
        self.send_message(msg)

        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 0)
