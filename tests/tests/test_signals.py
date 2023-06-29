from unittest.mock import patch

from django.test import TestCase

from django_yubin import settings
from django_yubin.storage_backends import DatabaseStorageBackend

from .base import MessageMixin


class TestSignals(MessageMixin, TestCase):
    def setUp(self):
        self.message = self.create_message()

    @patch.object(DatabaseStorageBackend, 'delete_message_data')
    def test_delete_message_storage_callback_active(self, delete_mock):
        settings.MAILER_STORAGE_DELETE = True
        self.message.delete()
        delete_mock.assert_called_once()

    @patch.object(DatabaseStorageBackend, 'delete_message_data')
    def test_delete_message_storage_callback_not_active(self, delete_mock):
        settings.MAILER_STORAGE_DELETE = False
        self.message.delete()
        delete_mock.assert_not_called()
