from unittest.mock import patch

from django.test import TestCase

from django_yubin import settings
from django_yubin.engine import send_db_message
from django_yubin.models import Blacklist, Message


class TestSendDBMessage(TestCase):
    """
    Tests engine function that sends db messages.
    """
    def setUp(self):
        self.message = Message.objects.create(
            to_address="johndoe@acmecorp.com",
            from_address="no-reply@acmecorp.com",
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            status=Message.STATUS_QUEUED,
        )

    def test_send_email_not_found(self):
        self.assertFalse(send_db_message(-1))

    def test_send_email_not_queued(self):
        self.message.status = Message.STATUS_SENT
        self.message.save()
        self.assertFalse(send_db_message(self.message.pk))

        last_log_action = self.message.log_set.first().action
        self.assertEqual(last_log_action, Message.STATUS_SENT)

    def test_send_db_message_blacklist(self):
        Blacklist.objects.create(email=self.message.to_address)

        self.assertFalse(send_db_message(self.message.pk))
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.STATUS_BLACKLISTED)

        last_log_action = self.message.log_set.first().action
        self.assertEqual(last_log_action, Message.STATUS_BLACKLISTED)

    def test_send_db_message_pause(self):
        pause_send_backup = settings.PAUSE_SEND
        settings.PAUSE_SEND = True

        self.assertFalse(send_db_message(self.message.pk))
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.STATUS_DISCARDED)

        last_log_action = self.message.log_set.first().action
        self.assertEqual(last_log_action, Message.STATUS_DISCARDED)

        settings.PAUSE_SEND = pause_send_backup

    @patch('django_yubin.engine.get_connection', side_effect=OSError('Mock error'))
    def test_send_db_message_fail(self, get_connection_mock):
        self.assertFalse(send_db_message(self.message.pk))
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.STATUS_FAILED)

        last_log_action = self.message.log_set.first().action
        self.assertEqual(last_log_action, Message.STATUS_FAILED)

    def test_send_db_message(self):
        self.assertTrue(send_db_message(self.message.pk))
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.STATUS_SENT)

        last_log_action = self.message.log_set.first().action
        self.assertEqual(last_log_action, Message.STATUS_SENT)
