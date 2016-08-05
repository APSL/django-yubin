# encoding: utf-8

import logging
import sys

from django.core.management.base import BaseCommand
from django.db import connection
from django_yubin import models, settings
from django_yubin.engine import send_all
from django_yubin.management.commands import create_handler


class Command(BaseCommand):
    help = 'Iterate the mail queue, attempting to send all mail.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-b',
            '--block_size',
            dest='block_size',
            type=int,
            default=500,
            help='The number of messages to iterate before checking the queue '
                 'again (in case new messages have been added while the queue '
                 'is being cleared).',
        )
        parser.add_argument(
            '-c',
            '--count',
            dest='count',
            action='store_true',
            default=False,
            help='Return the number of messages in the queue (without '
                 'actually sending any)',
        )

    def handle(self, verbosity, **options):
        # If this is just a count request the just calculate, report and exit.
        if options['count']:
            queued = models.QueuedMessage.objects.non_deferred().count()
            deferred = models.QueuedMessage.objects.deferred().count()
            sys.stdout.write('%s queued message%s (and %s deferred message%s).'
                             '\n' % (queued, queued != 1 and 's' or '',
                                     deferred, deferred != 1 and 's' or ''))
            sys.exit()

        # Send logged messages to the console.
        logger = logging.getLogger('django_yubin')
        handler = create_handler(verbosity)
        logger.addHandler(handler)

        # if PAUSE_SEND is turned on don't do anything.
        if not settings.PAUSE_SEND:
            send_all(options['block_size'], backend=settings.USE_BACKEND)
        else:
            logger = logging.getLogger('django_yubin.commands.send_mail')
            logger.warning("Sending is paused, exiting without sending "
                           "queued mail.")

        logger.removeHandler(handler)

        # Stop superfluous "unexpected EOF on client connection" errors in
        # Postgres log files caused by the database connection not being
        # explicitly closed.
        connection.close()
