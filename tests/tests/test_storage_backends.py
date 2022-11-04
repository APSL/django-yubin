from django.test import TestCase

from django_yubin import settings
from django_yubin.models import Message
from django_yubin.storage_backends import DatabaseStorageBackend, FileStorageBackend


class TestBaseStorageBackend(TestCase):
    storage_backend = NotImplemented

    @classmethod
    def setUpClass(cls):
        cls.storage_backend_backup = settings.MAILER_STORAGE_BACKEND
        settings.MAILER_STORAGE_BACKEND = cls.storage_backend

    @classmethod
    def tearDownClass(cls):
        settings.MAILER_STORAGE_BACKEND = cls.storage_backend_backup

    def setUp(self):
        self.message = Message.objects.create(
            to_address="johndoe@acmecorp.com",
            from_address="no-reply@acmecorp.com",
            subject="Lorem ipsum dolor sit amet",
            encoded_message="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
        )


class TestDatabaseStorageBackend(TestBaseStorageBackend):
    storage_backend = 'django_yubin.storage_backends.DatabaseStorageBackend'

    def test_get_encoded_message(self):
        backend_message = DatabaseStorageBackend.get_encoded_message(self.message)
        self.assertEqual(self.message.encoded_message, backend_message)
        self.assertEqual(self.message._encoded_message, backend_message)

    def test_set_encoded_message(self):
        new_value = 'Foo 🙂 mèssage'
        DatabaseStorageBackend.set_encoded_message(self.message, new_value)
        updated_value = DatabaseStorageBackend.get_encoded_message(self.message)
        self.assertEqual(updated_value, new_value)
        self.assertEqual(self.message.encoded_message, new_value)


class TestFileStorageBackend(TestBaseStorageBackend):
    storage_backend = 'django_yubin.storage_backends.FileStorageBackend'

    def test_get_encoded_message(self):
        backend_message = FileStorageBackend.get_encoded_message(self.message)
        self.assertEqual(self.message.encoded_message, backend_message)
        self.assertEqual(self.message._encoded_message, FileStorageBackend.get_path(self.message))

    def test_set_encoded_message(self):
        new_value = 'Foo 🙂 mèssage'
        FileStorageBackend.set_encoded_message(self.message, new_value)
        updated_value = FileStorageBackend.get_encoded_message(self.message)
        self.assertEqual(updated_value, new_value)
        self.assertEqual(self.message.encoded_message, new_value)
        self.assertEqual(self.message._encoded_message, FileStorageBackend.get_path(self.message))
