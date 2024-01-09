from datetime import timedelta
from email.mime.image import MIMEImage
from email.generator import _fmt
from unittest.mock import patch

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import TestCase
from django.utils import timezone

from django_yubin import tasks
from django_yubin.models import Message

from .base import MessageMixin


class TestMessage(MessageMixin, TestCase):

    def setUp(self):
        self.message = self.create_message()

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
        self.message.mark_as(Message.STATUS_IN_PROCESS)
        self.assertFalse(self.message.enqueue())

    def test_enqueue_exception(self):
        self.message.status = Message.STATUS_SENT
        self.message.save()
        backup = {
            'date_enqueued': self.message.date_enqueued,
            'enqueued_count': self.message.enqueued_count,
            'status': self.message.status,
        }
        self.assertFalse(self.message.enqueue())
        self.assertEqual(self.message.date_enqueued, backup["date_enqueued"])
        self.assertEqual(self.message.enqueued_count, backup["enqueued_count"])
        self.assertEqual(self.message.status, backup["status"])

    def test_enqueue_ok(self):
        with self.captureOnCommitCallbacks() as callbacks:
            self.assertTrue(self.message.enqueue())
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(callbacks[0].func, tasks.send_email.delay)

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

    def test_delete_old(self):
        days = 7
        message = self.create_message()
        message.date_created = timezone.now() - timedelta(days=days + 1)
        message.save()

        Message.delete_old(days)

        messages = Message.objects.all()
        self.assertEqual(len(messages), 1)
        self.assertGreaterEqual(messages[0].date_created, timezone.now() - timedelta(days=days))

    @patch("django.core.mail.message.generator.Generator._make_boundary")
    def test_get_email_message_roundtrip(self, mock_make_boundary):
        self.maxDiff = None

        def get_boundary(token: int):
            return ('=' * 15) + (_fmt % token) + '=='

        boundaries = [get_boundary(10), get_boundary(20), get_boundary(30), get_boundary(40)]

        def reset_mock():
            assert mock_make_boundary.call_count == 2
            mock_make_boundary.reset_mock(side_effect=True)
            mock_make_boundary.side_effect = boundaries

        mock_make_boundary.side_effect = boundaries

        ref = EmailMultiAlternatives(
            subject="Some subject",
            body="Plain text body",
            from_email="from@example.com",
            to=["to@example.com"],
            bcc=["bcc@example.com"],
            cc=["cc@example.com"],
            headers={"X-Custom": "custom-header"},
            reply_to=["reply-to@example.com"],
        )
        ref.attach_alternative(
            "<html><body><img src=\"cid:123456789\" /></body></html>",
            "text/html"
        )
        ref.mixed_subtype = "related"
        # add an inline cid image (PNG, white pixel)
        image = MIMEImage(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08"
            b"\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9"
            b"\x00\x00\x00\rIDAT\x18Wc\xf8\xff\xef\xdf\x7f\x00\t\xf6\x03\xfbW\xfe{\x1b"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image.add_header("Content-ID", "<123456789>")
        ref.attach(image)
        ref.attach("dummy.pdf", b"mock-data", "application/pdf")
        ref_msg = ref.message()
        assert ref_msg["Content-Type"].startswith("multipart/related")
        ref_as_string = ref_msg.as_string()
        reset_mock()
        ref_message_id = ref_msg["Message-ID"]
        ref_date = ref_msg["Date"]

        # construct model instance and reconstruct the django email message
        msg = Message(message_data=ref_as_string)
        reconstructed = msg.get_email_message()

        reconstructed_msg = reconstructed.message()

        with self.subTest(alternative="html"):
            self.assertEqual(len(reconstructed.alternatives), 1)
            self.assertEqual(
                reconstructed.alternatives[0],
                ("<html><body><img src=\"cid:123456789\" /></body></html>", "text/html")
            )

        # some tangible checks, but the kicker is really the string comparison
        for attr in ("subject", "body", "from_email", "to", "cc", "reply_to"):
            with self.subTest(msg_attr=attr):
                original = getattr(ref, attr)
                _reconstructed = getattr(reconstructed, attr)

                self.assertEqual(_reconstructed, original)

        with self.subTest("BCC"):
            # original message does not store BCC in headers (that beats the point)
            self.assertEqual(reconstructed.bcc, [])

        with self.subTest("custom headers"):
            custom_header = reconstructed.extra_headers.get("X-Custom")
            self.assertEqual(custom_header, "custom-header")

        # Special check for content type
        with self.subTest("mixed subtype"):
            content_type = reconstructed.message()["Content-Type"]
            self.assertTrue(content_type.startswith("multipart/related"))

        # Important to correlate messages in the logs with mail server logs/mail client
        # reported headers
        with self.subTest("message ID"):
            self.assertEqual(reconstructed_msg["Message-ID"], ref_message_id)

        with self.subTest("date"):
            self.assertEqual(reconstructed_msg["Date"], ref_date)

        with self.subTest("compare message as_string"):
            self.assertEqual(reconstructed_msg.as_string(), ref_as_string)
            reset_mock()

    def test_email_with_long_subject(self):
        email_message = EmailMessage(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
            "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            "Message body",
            'mail_from@abc.com',
            ['mail_to@abc.com']
        )

        message = Message.objects.create(
            to_address=','.join(email_message.to),
            cc_address=','.join(email_message.cc),
            bcc_address=','.join(email_message.bcc),
            from_address=email_message.from_email,
            subject=email_message.subject,
            message_data=email_message.message().as_string(),
        )

        parsed_message = message.get_email_message()

        self.assertNotIn("\n", parsed_message.subject)
