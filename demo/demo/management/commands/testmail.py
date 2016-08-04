#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--quantity',
            dest='qtt',
            default=1,
            help='Generates a number of fake mails for testing',
        )

    def handle(self, *args, **options):
        number = int(options['qtt'])
        for i in range(1, number + 1):
            send_mail('test %s' % i, 'body %s' % i, 'test@example.com',
                      ['recipient%s@example.com' % i])
        self.stdout.write('Generated')
