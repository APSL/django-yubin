#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

PRIORITY_EMAIL_NOW = 0
PRIORITY_HIGH = 1
PRIORITY_NORMAL = 3
PRIORITY_LOW = 5

RESULT_SENT = 0
RESULT_SKIPPED = 1
RESULT_FAILED = 2

PRIORITIES = {
    'now': PRIORITY_EMAIL_NOW,
    'high': PRIORITY_HIGH,
    'normal': PRIORITY_NORMAL,
    'low': PRIORITY_LOW,
}

PRIORITY_HEADER = 'X-Mail-Queue-Priority'

try:
    from django.core.mail import get_connection
    EMAIL_BACKEND_SUPPORT = True
except ImportError:
    # Django version < 1.2
    EMAIL_BACKEND_SUPPORT = False
