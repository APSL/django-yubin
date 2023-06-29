from django.test import TestCase

from django_yubin import settings
from django_yubin.models import Message
from django_yubin.storage_backends import (DatabaseStorageBackend, FileStorageBackend,
                                           StorageBackendException, db2file, file2db)

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

    def test_delete_message_data(self):
        self.assertIsNone(DatabaseStorageBackend.delete_message_data(self.message))


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

    def test_delete_message_data(self):
        FileStorageBackend.delete_message_data(self.message)
        with self.assertRaises(FileNotFoundError):
            FileStorageBackend.get_message_data(self.message)


class TestMigrations(MessageMixin, TestCase):
    def test_db2file(self):
        """
        The ``db2file`` migrates emails from database to filesystem.
        """
        db_message = self.create_message()
        db_message_data = db_message.message_data
        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'

        db2file()

        file_message = Message.objects.get(pk=db_message.pk)
        self.assertEqual(file_message.message_data, db_message_data)

        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'
        self.assertFalse(Message.objects.filter(storage=settings.MAILER_STORAGE_BACKEND).exists())

    def test_db2file_settings(self):
        with self.assertRaises(StorageBackendException):
            db2file()

    def test_file2db(self):
        """
        The ``file2db`` migrates emails from filesystem to database.
        """
        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'
        file_message = self.create_message()
        file_message_data = file_message.message_data
        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'

        file2db(delete=True)

        db_message = Message.objects.get(pk=file_message.pk)
        self.assertEqual(db_message.message_data, file_message_data)
        self.assertFalse(Message.objects.filter(
            storage='django_yubin.storage_backends.FileStorageBackend').exists())

    def test_file2db_settings(self):
        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'
        with self.assertRaises(StorageBackendException):
            file2db()
        settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'
