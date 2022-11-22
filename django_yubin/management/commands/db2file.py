from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from ... import settings as yubin_settings
from ...models import Message
from ...storage_backends import DatabaseStorageBackend, FileStorageBackend


class Command(BaseCommand):
    help = 'Migrate emails from DatabaseStorageBackend storage to FileStorageBackend.'

    def handle(self, *args, **options):
        self.check_settings()

        for message in Message.objects.all().only('pk', '_message_data'):
            db_message_data = DatabaseStorageBackend.get_message_data(message)
            DatabaseStorageBackend.set_message_data(message, data='')
            message.message_data = db_message_data
            message.save()
            self.stdout.write(f'Message {message.pk} migrated. Saved in {message._message_data}')

    def check_settings(self):
        backend = import_string(yubin_settings.MAILER_STORAGE_BACKEND)
        if backend != FileStorageBackend:
            raise CommandError(
                f'settings.MAILER_STORAGE_BACKEND should be {FileStorageBackend} instead of {backend}')
