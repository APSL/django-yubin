# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand

from ...messages import BasicHTMLEmailMessageView


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

        from_email = 'test@example.com'
        to = ['recipient@example.com']

        for i in range(1, number + 1):
            subject = 'Subject test %s ✉️ 🙂 àäá' % i
            content = 'Body test <strong>%s</strong> ✉️ 🙂 àäá.' % i
            message = BasicHTMLEmailMessageView(subject, content)
            message.send(from_email=from_email, to=to)

        # This output is checked in tests.
        self.stdout.write('Created email(s): %d' % number)
