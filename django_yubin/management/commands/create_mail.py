# encoding: utf-8

from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create fake mails for testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-q',
            '--quantity',
            dest='quantity',
            default=1,
            help='Number of fake mails to create.',
        )

    def handle(self, *args, **options):
        number = int(options['quantity'])
        for i in range(1, number + 1):
            send_mail(subject='test %s' % i,
                      message='body %s' % i,
                      from_email='test@example.com',
                      recipient_list=['recipient%s@example.com' % i],
                      html_message='body <strong>%s</strong>' % i)
        self.stdout.write('Created')
