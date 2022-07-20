from unittest.mock import patch

from django.test import TestCase
from django_yubin.backends import QueuedEmailBackend


@patch('django_yubin.backends.queue_email_message', return_value=1)
class TestBackend(TestCase):

    def test_send_no_messages(self, queue_email_message_mock):
        """
        Test that no messages are enqueued if no emails are passed.
        """
        sent = QueuedEmailBackend().send_messages([])
        self.assertEqual(sent, 0)
        self.assertFalse(queue_email_message_mock.called)

    def test_send_many_messages(self, queue_email_message_mock):
        """
        Test that all messages are passed to the enqueue function.
        """
        num_messages = 5
        sent = QueuedEmailBackend().send_messages(range(num_messages))
        self.assertEqual(sent, num_messages)
        self.assertEqual(queue_email_message_mock.call_count, num_messages)
