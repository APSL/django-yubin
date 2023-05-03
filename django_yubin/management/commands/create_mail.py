import os

from django.core.management.base import BaseCommand

from ...message_views import BasicHTMLAttachmentEmailMessageView


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

        from_email = 'from@example.com'
        to = ['to1@example.com', 'to2@example.com']
        cc = ['cc@example.com']
        bcc = ['bcc@example.com']

        for i in range(1, number + 1):
            subject = 'Subject test %s ✉️ 🙂 àäá' % i
            content = 'Body test <strong>%s</strong> ✉️ 🙂 àäá.' % i
            attachment_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sample.pdf')
            with open(attachment_path, 'rb') as f:
                attachment = f.read()
            filename = 'sample.pdf'
            mimetype = 'application/pdf'
            message = BasicHTMLAttachmentEmailMessageView(subject, content, attachment, filename, mimetype)
            message.send(from_email=from_email, to=to, cc=cc, bcc=bcc)

        # This output is checked in tests.
        self.stdout.write('Created email(s): %d' % number)
