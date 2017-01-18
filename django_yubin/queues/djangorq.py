#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import django_rq

from django_yubin.queues.base import QueueBase
from django_yubin import settings


@django_rq.job(settings.YUBIN_QUEUE_DJANGORQ_QUEUENAME)
def yubin_queue_system_enqueue(message, priority):
    pass


class QueueSystem(QueueBase):
    """Using DjangoRQ"""

    def enqueue(self, message, priority):
        yubin_queue_system_enqueue.delay(message, priority)