from django.core.management.base import BaseCommand

from ...models import Message


class Command(BaseCommand):
    help = 'Delete the mails created before -d days (default 90)'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--days',
            dest='days',
            type=int,
            default=90,
            help="Cleanup mails older than this many days, defaults to 90.",
        )

    def handle(self, verbosity, **options):
        deleted, cutoff_date = Message.delete_old(options['days'])
        self.stdout.write("Deleted %s mails created before %s " % (deleted[0], cutoff_date))
