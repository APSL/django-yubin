#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

import logging
import time
from io import StringIO

from django.conf import settings as django_settings
from django.core import mail
from django.test import TestCase

from lockfile import FileLock

from django_yubin import engine, settings, models, constants, queue_email_message

from .base import MailerTestCase


class LockTest(TestCase):
    """
    Tests for Django Mailer trying to send mail when the lock is already in
    place.
    """

    def setUp(self):
        # Create somewhere to store the log debug output.
        self.output = StringIO()
        # Create a log handler which can capture the log debug output.
        self.handler = logging.StreamHandler(self.output)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        self.handler.setFormatter(formatter)
        # Add the log handler.
        logger = logging.getLogger('django_yubin')
        logger.addHandler(self.handler)

        # Set the LOCK_WAIT_TIMEOUT to the default value.
        self.original_timeout = settings.LOCK_WAIT_TIMEOUT
        settings.LOCK_WAIT_TIMEOUT = 0

        # Use a test lock-file name in case something goes wrong, then emulate
        # that the lock file has already been acquired by another process.
        self.original_lock_path = engine.LOCK_PATH
        engine.LOCK_PATH += '.mailer-test'
        self.lock = FileLock(engine.LOCK_PATH)
        self.lock.unique_name += '.mailer_test'
        self.lock.acquire(0)

    def tearDown(self):
        # Remove the log handler.
        logger = logging.getLogger('django_yubin')
        logger.removeHandler(self.handler)

        # Revert the LOCK_WAIT_TIMEOUT to it's original value.
        settings.LOCK_WAIT_TIMEOUT = self.original_timeout

        # Revert the lock file unique name
        engine.LOCK_PATH = self.original_lock_path
        self.lock.release()

    def test_locked(self):
        # Acquire the lock so that send_all will fail.
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[-1].strip(),
                         'Lock already in place. Exiting.')
        # Try with a timeout.
        settings.LOCK_WAIT_TIMEOUT = .1
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[-1].strip(),
                         'Waiting for the lock timed out. Exiting.')

    def test_locked_timeoutbug(self):
        # We want to emulate the lock acquiring taking no time, so the next
        # three calls to time.time() always return 0 (then set it back to the
        # real function).
        original_time = time.time
        global time_call_count
        time_call_count = 0

        def fake_time():
            global time_call_count
            time_call_count = time_call_count + 1
            if time_call_count >= 3:
                time.time = original_time
            return 0

        time.time = fake_time
        try:
            engine.send_all()
            self.output.seek(0)
            self.assertEqual(self.output.readlines()[-1].strip(),
                             'Lock already in place. Exiting.')
        finally:
            time.time = original_time


class SendMessageTest(MailerTestCase):
    """
    Tests engine functions that send messages.
    """

    def setUp(self):
        # Set EMAIL_BACKEND
        super(SendMessageTest, self).setUp()
        if hasattr(django_settings, 'EMAIL_BACKEND'):
            self.old_email_backend = django_settings.EMAIL_BACKEND
        else:
            self.old_email_backend = None
        django_settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.' \
                                        'EmailBackend'

        # Create somewhere to store the log debug output.
        self.output = StringIO()

        # Create a log handler which can capture the log debug output.
        self.handler = logging.StreamHandler(self.output)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        self.handler.setFormatter(formatter)

        # Add the log handler.
        logger = logging.getLogger('django_yubin')
        logger.addHandler(self.handler)

    def tearDown(self):
        # Restore EMAIL_BACKEND
        super(SendMessageTest, self).tearDown()
        if self.old_email_backend:
            django_settings.EMAIL_BACKEND = self.old_email_backend
        else:
            delattr(django_settings, 'EMAIL_BACKEND')

        # Remove the log handler.
        logger = logging.getLogger('django_yubin')
        logger.removeHandler(self.handler)

    def test_send_queued_message(self):
        self.queue_message()
        self.assertEqual(models.QueuedMessage.objects.count(), 1)
        q_message = models.QueuedMessage.objects.first()
        result = engine.send_queued_message(q_message)
        self.assertEqual(result, constants.RESULT_SENT)

    def test_pause_queued_message(self):
        self.queue_message()
        self.assertEqual(models.QueuedMessage.objects.count(), 1)
        q_message = models.QueuedMessage.objects.first()
        _original, settings.PAUSE_SEND = settings.PAUSE_SEND, True
        result = engine.send_queued_message(q_message)
        settings.PAUSE_SEND = _original
        self.assertEqual(result, constants.RESULT_SKIPPED)

    def test_send_message(self):
        email_message = mail.EmailMessage('subject', 'body', 'from@email.com',
                                          ['to@email.com'])
        result = engine.send_message(email_message)
        self.assertEqual(result, constants.RESULT_SENT)

    def test_pause_send_message(self):
        email_message = mail.EmailMessage('subject', 'body', 'from@email.com',
                                          ['to@email.com'])
        _original, settings.PAUSE_SEND = settings.PAUSE_SEND, True
        result = engine.send_message(email_message)
        settings.PAUSE_SEND = _original
        self.assertEqual(result, constants.RESULT_SKIPPED)

    def test_send_all_non_empty_queue(self):
        msg = mail.EmailMessage('subject', 'body', 'from@email.com',
                                ['to@email.com'])
        queue_email_message(msg)
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[-1].strip()[-8:], 'seconds.')

    def test_send_all_empty_queue(self):
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[2].strip(),
                         'No messages in queue.')
