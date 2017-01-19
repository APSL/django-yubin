#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

from django.core import mail
from django.test import TestCase

from django_yubin import queue_email_message
from django_yubin import settings
from django_yubin.models import QueuedMessage

from django_rq import get_worker


class TestQueuesDjangoRq(TestCase):

    def setUp(self):
        super(TestQueuesDjangoRq, self).setUp()
        settings.QUEUE_SYSTEM_NAME = 'djangorq'

    def test_djangorq(self):
        worker = get_worker()
        queue = worker.queues[0]
        queue.empty()
        self.assertEqual(len(queue.jobs), 0)
        self.assertEqual(QueuedMessage.objects.all().count(), 0)

        msg = mail.EmailMessage(
            subject='subject queue',
            body='body',
            from_email='mail_from@abc.com',
            to=['mail_to@djangorq.com'],
            headers={'X-Mail-Queue-Priority': 'high'}
        )
        queue_email_message(msg)

        # Checking enqueued messages...
        self.assertEqual(len(queue.jobs), 1)

        # Processing all jobs
        worker.work(burst=True)

        self.assertEqual(len(queue.jobs), 0)
        self.assertEqual(QueuedMessage.objects.all().count(), 0)
