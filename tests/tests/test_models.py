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

    def test_mark_as_without_log(self):
        self.message.mark_as(Message.STATUS_FAILED)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)

        logs_count = self.message.log_set.all().count()
        self.assertEqual(logs_count, 0)

    def test_mark_as_with_log(self):
        log_message = "test mark"

        self.message.mark_as(Message.STATUS_FAILED, log_message)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)

        logs = self.message.log_set.all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].log_message, log_message)

    def test_mark_as_sent(self):
        now = timezone.now()
        sent_count = self.message.sent_count
        self.message.mark_as(Message.STATUS_SENT)
        self.assertEqual(self.message.status, Message.STATUS_SENT)
        self.assertGreater(self.message.date_sent, now)
        self.assertEqual(self.message.sent_count, sent_count+1)

    def test_mark_as_queued(self):
        now = timezone.now()
        enqueued_count = self.message.enqueued_count
        self.message.mark_as(Message.STATUS_QUEUED)
        self.assertEqual(self.message.status, Message.STATUS_QUEUED)
        self.assertGreater(self.message.date_enqueued, now)
        self.assertEqual(self.message.enqueued_count, enqueued_count+1)

    def test_enqueue_wrong_status(self):
        self.message.mark_as(Message.STATUS_QUEUED)
        self.assertFalse(self.message.enqueue())

    @patch("django_yubin.tasks.send_email.delay", side_effect=Exception)
    def test_enqueue_exception(self, send_email_mock):
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
    def test_enqueue_ok(self, send_email_mock):
        self.assertTrue(self.message.enqueue())
        self.assertEqual(self.message.status, Message.STATUS_QUEUED)

    def test_retry_messages_none(self):
        enqueued, failed = Message.retry_messages()
        self.assertEqual((enqueued, failed), (0, 0))

    def test_retry_messages(self):
        self.message.status = Message.STATUS_FAILED
        self.message.save()
        enqueued, failed = Message.retry_messages()
        self.assertEqual((enqueued, failed), (1, 0))

    def test_retry_messages_max_retries(self):
        self.message.status = Message.STATUS_FAILED
        self.message.enqueued_count = 3
        self.message.save()
        enqueued, failed = Message.retry_messages()
        self.assertEqual((enqueued, failed), (0, 0))

    @patch("django_yubin.tasks.send_email.delay", side_effect=Exception('Mock exception'))
    def test_retry_messages_enqueue_failed(self, send_mail_mock):
        self.message.status = Message.STATUS_FAILED
        self.message.save()
        enqueued, failed = Message.retry_messages()
        self.assertEqual((enqueued, failed), (0, 1))
