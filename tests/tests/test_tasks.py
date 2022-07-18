from unittest.mock import patch

from django.test import TestCase

from django_yubin.models import Message
from django_yubin.engine import send_db_message
from django_yubin.tasks import send_email


@patch('django_yubin.engine.send_db_message', side_effect=send_db_message)
class TestTasks(TestCase):

    def testSendEmailNotFound(self, send_db_message_mock):
        send_email(-1)
        self.assertFalse(send_db_message_mock.called)

    def testSendEmailCannotBeSent(self, send_db_message_mock):
        message = Message.objects.create(
            to_address='',
            from_address='',
            subject='',
            encoded_message='',
            status=Message.STATUS_SENT,
        )
        send_email(message.pk)
        self.assertFalse(send_db_message_mock.called)
        message.refresh_from_db()
        self.assertEqual(message.status, Message.STATUS_SENT)

    def testSendEmailSuccess(self, send_db_message_mock):
        message = Message.objects.create(
            to_address='johndoe@acmecorp.com',
            from_address='no-reply@acmecorp.com',
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        )
        send_email(message.pk)
        self.assertTrue(send_db_message_mock.called)
        message.refresh_from_db()
        self.assertEqual(message.status, Message.STATUS_SENT)

    def testSendEmailSendTwice(self, send_db_message_mock):
        message = Message.objects.create(
            to_address='johndoe@acmecorp.com',
            from_address='no-reply@acmecorp.com',
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        )
        send_email(message.pk)
        self.assertTrue(send_db_message_mock.called)
        message.refresh_from_db()
        self.assertEqual(message.status, Message.STATUS_SENT)
        send_email(message.pk)
        self.assertEqual(send_db_message_mock.call_count, 1)
