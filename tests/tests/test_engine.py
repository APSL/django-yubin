from socket import error as SocketError
from unittest.mock import patch

from django_yubin import settings
from django_yubin.engine import send_db_message
from django_yubin.models import Blacklist, Message

from .base import MailerTestCase


class TestSendDBMessage(MailerTestCase):
    """
    Tests engine function that sends db messages.
    """
    def setUp(self):
        self.message = Message.objects.create(
            to_address="johndoe@acmecorp.com",
            from_address="no-reply@acmecorp.com",
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        )

    def test_send_db_message(self):
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_SENT)

    def test_send_db_message_blacklist_param(self):
        send_db_message(self.message, blacklist=[self.message.to_address])
        self.assertEqual(self.message.status, Message.STATUS_BLACKLISTED)

    def test_send_db_message_blacklist_db(self):
        Blacklist.objects.create(email=self.message.to_address)
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_BLACKLISTED)

    def test_send_db_message_pause(self):
        pause_send_backup = settings.PAUSE_SEND
        settings.PAUSE_SEND = True

        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_DISCARDED)

        settings.PAUSE_SEND = pause_send_backup

    @patch('django_yubin.engine.get_connection', side_effect=SocketError)
    def test_send_db_message_fail(self, get_connection_mock):
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)
