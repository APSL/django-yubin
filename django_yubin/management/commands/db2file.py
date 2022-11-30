from django.core.management.base import BaseCommand

from ...storage_backends import db2file


class Command(BaseCommand):
    help = 'Migrate emails from DatabaseStorageBackend storage to FileStorageBackend.'

    def handle(self, *args, **options):
        db2file()
