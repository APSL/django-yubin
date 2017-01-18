#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------


class QueueBase(object):
    """Main interficie"""

    def enqueue(self, message):
        raise NotImplementedError