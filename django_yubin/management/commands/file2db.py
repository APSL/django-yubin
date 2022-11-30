from django.core.management.base import BaseCommand

from ...storage_backends import file2db


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
        file2db(delete)
