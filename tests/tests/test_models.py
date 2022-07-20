from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from django_yubin.models import Message


class TestMessage(TestCase):

    def setUp(self):
        self.message = Message.objects.create(
            to_address="johndoe@acmecorp.com",
            from_address="no-reply@acmecorp.com",
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        )

    def testMarkAsWithoutLog(self):
        self.message.mark_as(Message.STATUS_FAILED)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)

        logs_count = self.message.log_set.all().count()
        self.assertEqual(logs_count, 0)

    def testMarkAsWithLog(self):
        log_message = "test mark"

        self.message.mark_as(Message.STATUS_FAILED, log_message)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)

        logs = self.message.log_set.all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].log_message, log_message)

    def testMarkAsSent(self):
        now = timezone.now()
        sent_count = self.message.sent_count
        self.message.mark_as(Message.STATUS_SENT)
        self.assertEqual(self.message.status, Message.STATUS_SENT)
        self.assertGreater(self.message.date_sent, now)
        self.assertEqual(self.message.sent_count, sent_count+1)

    def testMarkAsQueued(self):
        now = timezone.now()
        enqueued_count = self.message.enqueued_count
        self.message.mark_as(Message.STATUS_QUEUED)
        self.assertEqual(self.message.status, Message.STATUS_QUEUED)
        self.assertGreater(self.message.date_enqueued, now)
        self.assertEqual(self.message.enqueued_count, enqueued_count+1)

    def testEnqueueWrongStatus(self):
        self.message.mark_as(Message.STATUS_QUEUED)
        self.assertFalse(self.message.enqueue())

    @patch("django_yubin.tasks.send_email.delay", side_effect=Exception)
    def testEnqueueException(self, send_email_mock):
        backup = {
            'date_enqueued': self.message.date_enqueued,
            'enqueued_count': self.message.enqueued_count,
            'status': self.message.status,
        }
        self.assertFalse(self.message.enqueue())
        self.assertEqual(self.message.date_enqueued, backup["date_enqueued"])
        self.assertEqual(self.message.enqueued_count, backup["enqueued_count"])
        self.assertEqual(self.message.status, backup["status"])

    @patch("django_yubin.tasks.send_email.delay")
    def testEnqueueOK(self, send_email_mock):
        self.assertTrue(self.message.enqueue())
        self.assertEqual(self.message.status, Message.STATUS_QUEUED)
