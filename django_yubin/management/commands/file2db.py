from django.core.management.base import BaseCommand, CommandError

from ...storage_backends import file2db, StorageBackendException


class Command(BaseCommand):
    help = 'Migrate emails from FileStorageBackend storage to DatabaseStorageBackend.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete files from the FileStorageBackend.',
        )

    def handle(self, *args, **options):
        delete = options['delete']
        try:
            file2db(delete)
        except StorageBackendException as e:
            raise CommandError(e)
