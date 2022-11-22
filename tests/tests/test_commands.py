from six import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from django_yubin import settings as yubin_settings
from django_yubin.models import Message

from .base import MessageMixin


class TestCommands(MessageMixin, TestCase):
    """
    A test case for Django management commands.
    """
    def test_create_mail(self):
        """
        The ``create_mail`` command create new mails.
        """
        out = StringIO()
        quantity = 2
        call_command('create_mail', quantity=quantity, stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(quantity, created)

    def test_send_test_mail(self):
        """
        The ``send_test_mail`` sends a test mail to test connection params
        """
        out = StringIO()
        call_command('send_test_mail', to='test@test.com', stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(1, created)

    def test_send_test_no_email(self):
        """
        The ``send_test_mail`` without to email. Expect an error.
        """
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass

    def test_send_test_no_admins(self):
        """
        The ``send_test_mail`` without to email. Expect an error.
        """
        settings.ADMINS = []
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass

    def test_db2file(self):
        """
        The ``db2file`` migrates emails from database to filesystem.
        """
        db_message = self.create_message()
        db_message_data = db_message.message_data
        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'

        out = StringIO()
        call_command('db2file', stdout=out)
        self.assertIn(str(db_message.pk), out.getvalue())

        file_message = Message.objects.get(pk=db_message.pk)
        self.assertEqual(file_message.message_data, db_message_data)

        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'

    def test_db2file_settings(self):
        with self.assertRaises(CommandError):
            call_command('db2file')

    def test_file2db(self):
        """
        The ``file2db`` migrates emails from filesystem to database.
        """
        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'
        file_message = self.create_message()
        file_message_data = file_message.message_data
        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'

        out = StringIO()
        call_command('file2db', '--delete', stdout=out)
        self.assertIn(str(file_message.pk), out.getvalue())

        db_message = Message.objects.get(pk=file_message.pk)
        self.assertEqual(db_message.message_data, file_message_data)

    def test_file2db_settings(self):
        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.FileStorageBackend'
        with self.assertRaises(CommandError):
            call_command('file2db')
        yubin_settings.MAILER_STORAGE_BACKEND = 'django_yubin.storage_backends.DatabaseStorageBackend'
