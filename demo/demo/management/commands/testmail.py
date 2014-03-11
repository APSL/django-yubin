#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------


from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.core.mail import send_mail

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quantity',
            dest='qtt',
            default=False,
            help = 'Generates a number of fake mails for testing'
    ),
    )

    def handle(self, *args, **options):
        number=int(options['qtt'])
        for i in range(0, number):
            send_mail('test %s' %i , 'body %s' % i,
                'test@example.com', ['recipient%s@example.com' %i, ])
        self.stdout.write('Generated')

