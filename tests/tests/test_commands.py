#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

import datetime
import re
import time
import json

from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.conf import settings
from django.utils.timezone import now

from django_yubin import models
from six import StringIO

from .base import MailerTestCase


class TestCommands(MailerTestCase):
    """
    A test case for management commands provided by django-mailer.

    """
    def test_send_mail(self):
        """
        The ``send_mail`` command initiates the sending of messages in the
        queue.

        """
        # No action is taken if there are no messages.
        call_command('send_mail', verbosity='0')
        # Any (non-deferred) queued messages will be sent.
        self.queue_message()
        self.queue_message()
        self.queue_message(subject='deferred')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 3)
        self.assertEqual(len(mail.outbox), 0)
        call_command('send_mail', verbosity='0')
        self.assertEqual(queued_messages.count(), 1)

    def test_send_mail_limit_0(self):
        """
        The ``send_mail`` command initiates the sending of messages in the
        queue. The number to send can be limited, 0 = no limit.

        """
        # No action is taken if there are no messages.
        call_command('send_mail', verbosity='0')
        # Only 1 (non-deferred) queued message will be sent.
        self.queue_message()
        self.queue_message()
        self.queue_message()
        self.queue_message(subject='deferred')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 4)
        self.assertEqual(len(mail.outbox), 0)
        call_command('send_mail', verbosity='0', message_limit=0)
        self.assertEqual(queued_messages.count(), 1)

    def test_send_mail_limit_2(self):
        """
        The ``send_mail`` command initiates the sending of messages in the
        queue. The number to send can be limited.

        """
        # No action is taken if there are no messages.
        call_command('send_mail', verbosity='0')
        # Only 1 (non-deferred) queued message will be sent.
        self.queue_message()
        self.queue_message()
        self.queue_message()
        self.queue_message(subject='deferred')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 4)
        self.assertEqual(len(mail.outbox), 0)
        call_command('send_mail', verbosity='0', message_limit=2)
        self.assertEqual(queued_messages.count(), 2)

    def test_send_mail_limit_10(self):
        """
        The ``send_mail`` command initiates the sending of messages in the
        queue. The number to send can be limited. Numbers higher than queue should be fine

        """
        # No action is taken if there are no messages.
        call_command('send_mail', verbosity='0')
        # Only 1 (non-deferred) queued message will be sent.
        self.queue_message()
        self.queue_message()
        self.queue_message()
        self.queue_message(subject='deferred')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        queued_messages = models.QueuedMessage.objects.all()
        self.assertEqual(queued_messages.count(), 4)
        self.assertEqual(len(mail.outbox), 0)
        call_command('send_mail', verbosity='0', message_limit=10)
        self.assertEqual(queued_messages.count(), 1)

    def test_retry_deferred(self):
        """
        The ``retry_deferred`` command places deferred messages back in the
        queue.

        """
        self.queue_message()
        self.queue_message(subject='deferred')
        self.queue_message(subject='deferred 2')
        self.queue_message(subject='deferred 3')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        non_deferred_messages = models.QueuedMessage.objects.non_deferred()
        # Deferred messages are returned to the queue (nothing is sent).
        self.assertEqual(non_deferred_messages.count(), 1)
        call_command('retry_deferred', verbosity='0')
        self.assertEqual(non_deferred_messages.count(), 4)
        self.assertEqual(len(mail.outbox), 0)
        # Check the --max-retries logic.
        models.QueuedMessage.objects.filter(
            message__subject='deferred').update(deferred=now(), retries=2)
        models.QueuedMessage.objects.filter(
            message__subject='deferred 2').update(deferred=now(), retries=3)
        models.QueuedMessage.objects.filter(
            message__subject='deferred 3').update(deferred=now(), retries=4)
        self.assertEqual(non_deferred_messages.count(), 1)
        call_command('retry_deferred', verbosity='0', max_retries=3)
        self.assertEqual(non_deferred_messages.count(), 3)

    def test_status_mail(self):
        """
        The ``status_mail`` should return a string that matches:
            (?P<queued>\d+)/(?P<deferred>\d+)/(?P<seconds>\d+)

        Also it checks the json output format.
        """
        re_string = r"(?P<queued>\d+)/(?P<deferred>\d+)/(?P<seconds>\d+)"
        p = re.compile(re_string)

        self.queue_message(subject="test")
        self.queue_message(subject='deferred')
        self.queue_message(subject='deferred 2')
        self.queue_message(subject='deferred 3')
        models.QueuedMessage.objects.filter(
            message__subject__startswith='deferred').update(deferred=now())
        models.QueuedMessage.objects.non_deferred()
        time.sleep(1)
        # Deferred messages are returned to the queue (nothing is sent).
        out = StringIO()
        call_command('status_mail', verbosity='0', stdout=out)
        result = out.getvalue()
        m = p.match(result)
        self.assertTrue(m, "Output does not include expected r.e.")
        v = m.groupdict()
        self.assertTrue(v['queued'], "1")
        self.assertEqual(v['deferred'], "3")
        self.assertTrue(int(v['seconds']) >= 1)

        # Testing json output
        out = StringIO()
        call_command('status_mail', '--json-format', verbosity='0', stdout=out)
        result = json.loads(out.getvalue())
        self.assertEqual(result['queued'], 1)
        self.assertEqual(result['deferred'], 3)
        self.assertTrue(result['seconds'] >= 1)

    def test_cleanup_mail(self):
        """
        The ``cleanup_mail`` command deletes mails older than a specified
        amount of days
        """
        today = datetime.date.today()
        self.assertEqual(models.Message.objects.count(), 0)
        # new message (not to be deleted)
        models.Message.objects.create()
        prev = today - datetime.timedelta(31)
        # new message (old)
        models.Message.objects.create(date_created=prev)
        call_command('cleanup_mail', days=30)
        self.assertEqual(models.Message.objects.count(), 1)

    def test_create_mail(self):
        """
        The ``create_mail`` command create new mails.
        """
        out = StringIO()
        quantity = 2
        call_command('create_mail', quantity=quantity, stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(quantity, created)

    def test_send_test_mail(self):
        """
        The ``send_test_mail`` sends a test mail to test connection params
        """
        out = StringIO()
        self.assertEqual(models.Message.objects.count(), 0)
        call_command('send_test_mail', to='test@test.com', stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(1, created)

    def test_send_test_no_email(self):
        """
        The ``send_test_mail`` without to email. Expect en error.
        """
        self.assertEqual(models.Message.objects.count(), 0)
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass

    def test_send_test_no_admins(self):
        """
        The ``send_test_mail`` without to email. Expect en error.
        """
        settings.ADMINS = []
        self.assertEqual(models.Message.objects.count(), 0)
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass
