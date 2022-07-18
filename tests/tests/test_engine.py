from socket import error as SocketError
from unittest.mock import patch

from django_yubin import settings
from django_yubin.engine import send_db_message
from django_yubin.models import Blacklist, Message

from .base import MailerTestCase


class SendDBMessageTest(MailerTestCase):
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

    def testSendDBMessage(self):
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_SENT)

    def testSendDBMessageBlacklistParam(self):
        send_db_message(self.message, blacklist=[self.message.to_address])
        self.assertEqual(self.message.status, Message.STATUS_BLACKLISTED)

    def testSendDBMessageBlacklistDB(self):
        Blacklist.objects.create(email=self.message.to_address)
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_BLACKLISTED)

    def testSendDBMessagePause(self):
        pause_send_backup = settings.PAUSE_SEND
        settings.PAUSE_SEND = True

        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_DISCARDED)

        settings.PAUSE_SEND = pause_send_backup

    @patch('django_yubin.engine.get_connection', side_effect=SocketError)
    def testSendDBMessageFail(self, get_connection_mock):
        send_db_message(self.message)
        self.assertEqual(self.message.status, Message.STATUS_FAILED)
