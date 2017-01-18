#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from django_yubin.queues.base import QueueBase
from django_yubin.models import QueuedMessage


class QueueSystem(QueueBase):
    """Use internal database model for enqueue messages"""

    def enqueue(self, message, priority):
        queued_message = QueuedMessage(message=message)
        if priority:
            queued_message.priority = priority
        queued_message.save()
