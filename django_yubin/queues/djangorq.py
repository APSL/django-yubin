#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import django_rq

from django_yubin import settings
from django_yubin.queues.utils import send_msg_or_internal_enqueue


@django_rq.job(settings.DJANGORQ_QUEUE)
def yubin_queue_system_enqueue(message, priority):
    send_msg_or_internal_enqueue(message, priority)


class QueueSystem(object):
    """Using DjangoRQ"""

    def enqueue(self, message, priority):
        yubin_queue_system_enqueue.delay(message, priority)
