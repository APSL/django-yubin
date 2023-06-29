from django.core.management.base import BaseCommand, CommandError

from ...storage_backends import db2file, StorageBackendException


class Command(BaseCommand):
    help = 'Migrate emails from DatabaseStorageBackend storage to FileStorageBackend.'

    def handle(self, *args, **options):
        try:
            db2file()
        except StorageBackendException as e:
            raise CommandError(e)
