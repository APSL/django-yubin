"""
This command returns the status of the queue in the format:
    queued/deferred/seconds

where:
    queued      is the number of queued messages we have actually
    deferred    number of deferred messages we have actually
    seconds     age in seconds of the oldest messages

Example:

    2/0/10

means we have 2 queued messages, 0 defered messaged and than the oldest message
in the queue is just 2 seconds old.
"""

from django.core.management.base import NoArgsCommand
from django_yubin.models import QueuedMessage
import sys
try:
    from django.utils.timezone import now
except ImportError:
    import datetime
    now = datetime.datetime.now

try:
    from django.core.mail import get_connection
    EMAIL_BACKEND_SUPPORT = True
except ImportError:
    # Django version < 1.2
    EMAIL_BACKEND_SUPPORT = False


class Command(NoArgsCommand):
    help = "Returns a strig with the queue status as queued/deferred/seconds"

    def handle_noargs(self, *args, **kwargs):
        # If this is just a count request the just calculate, report and exit.
        queued = QueuedMessage.objects.non_deferred().count()
        deferred = QueuedMessage.objects.deferred().count()
        try:
            oldest = QueuedMessage.objects.non_deferred().order_by('date_queued')[0]
            seconds = (now() - oldest.date_queued.replace(tzinfo=None)).seconds
        except (IndexError, QueuedMessage.DoesNotExist):
            seconds = 0
        sys.stdout.write('%s/%s/%s\n"' % (queued, deferred, seconds))
        sys.exit()
