from django.test import TestCase

from django_yubin import settings
from django_yubin.storage_backends import DatabaseStorageBackend, FileStorageBackend

from .base import MessageMixin


class TestBaseStorageBackend(MessageMixin, TestCase):
    storage_backend = NotImplemented

    @classmethod
    def setUpClass(cls):
        cls.storage_backend_backup = settings.MAILER_STORAGE_BACKEND
        settings.MAILER_STORAGE_BACKEND = cls.storage_backend

    @classmethod
    def tearDownClass(cls):
        settings.MAILER_STORAGE_BACKEND = cls.storage_backend_backup

    def setUp(self):
        self.message = self.create_message()


class TestDatabaseStorageBackend(TestBaseStorageBackend):
    storage_backend = 'django_yubin.storage_backends.DatabaseStorageBackend'

    def test_get_message_data(self):
        backend_message = DatabaseStorageBackend.get_message_data(self.message)
        self.assertEqual(self.message.message_data, backend_message)
        self.assertEqual(self.message._message_data, backend_message)

    def test_set_message_data(self):
        new_value = 'Foo 🙂 mèssage'
        DatabaseStorageBackend.set_message_data(self.message, new_value)
        updated_value = DatabaseStorageBackend.get_message_data(self.message)
        self.assertEqual(updated_value, new_value)
        self.assertEqual(self.message.message_data, new_value)


class TestFileStorageBackend(TestBaseStorageBackend):
    storage_backend = 'django_yubin.storage_backends.FileStorageBackend'

    def test_get_message_data(self):
        backend_message = FileStorageBackend.get_message_data(self.message)
        self.assertEqual(self.message.message_data, backend_message)
        self.assertEqual(self.message._message_data, FileStorageBackend.get_path(self.message))

    def test_set_message_data(self):
        new_value = 'Foo 🙂 mèssage'
        FileStorageBackend.set_message_data(self.message, new_value)
        updated_value = FileStorageBackend.get_message_data(self.message)
        self.assertEqual(updated_value, new_value)
        self.assertEqual(self.message.message_data, new_value)
        self.assertEqual(self.message._message_data, FileStorageBackend.get_path(self.message))
