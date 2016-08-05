# encoding: utf-8

from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate fake mails for testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-q',
            '--quantity',
            dest='quantity',
            default=1,
            help='Number of fake mails to generate.',
        )

    def handle(self, *args, **options):
        number = int(options['quantity'])
        for i in range(1, number + 1):
            send_mail('test %s' % i, 'body %s' % i, 'test@example.com',
                      ['recipient%s@example.com' % i])
        self.stdout.write('Generated')
