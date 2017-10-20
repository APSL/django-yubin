# encoding: utf-8

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
        for i in range(1, number + 1):
            BasicHTMLEmailMessageView(
                subject='Subject test %s' % i,
                content=u'Body test <strong>%s</strong> ✉️ 🙂 àäá.' % i,
            ).send(
                from_email='test@example.com',
                to=['recipient%s@example.com' % i],
            )
        self.stdout.write('Created %d email(s).' % number)
