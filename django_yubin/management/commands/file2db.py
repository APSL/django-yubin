from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from ... import settings as yubin_settings
from ...models import Message
from ...storage_backends import DatabaseStorageBackend, FileStorageBackend


class Command(BaseCommand):
    help = 'Migrate emails from FileStorageBackend storage to DatabaseStorageBackend.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete files from the FileStorageBackend.',
        )

    def handle(self, *args, **options):
        self.check_settings()
        delete = options['delete']

        for message in Message.objects.all().only('pk', '_message_data'):
            file_message_path = FileStorageBackend.get_path(message)
            file_message_data = FileStorageBackend.get_message_data(message)
            message.message_data = file_message_data
            message.save()
            self.stdout.write(f'Message {message.pk} migrated')
            if delete:
                FileStorageBackend.storage.delete(file_message_path)
                self.stdout.write(f'File {file_message_path} deleted from FileStorageBackend')

    def check_settings(self):
        backend = import_string(yubin_settings.MAILER_STORAGE_BACKEND)
        if backend != DatabaseStorageBackend:
            raise CommandError(
                f'settings.MAILER_STORAGE_BACKEND should be {DatabaseStorageBackend} instead of {backend}')
