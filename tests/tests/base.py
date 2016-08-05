#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

import six
from distutils.version import StrictVersion

import django
from django.core import mail
from django.test import TestCase

from django_yubin import queue_email_message


class FakeConnection(object):
    """
    A fake SMTP connection which diverts emails to the test buffer rather than
    sending.

    """
    def sendmail(self, *args, **kwargs):
        """
        Divert an email to the test buffer.

        """
        # FUTURE: the EmailMessage attributes could be found by introspecting
        # the encoded message.
        message = mail.EmailMessage('SUBJECT', 'BODY', 'FROM', ['TO'])
        mail.outbox.append(message)


class MailerTestCase(TestCase):
    """
    A base class for Django Mailer test cases which diverts emails to the test
    buffer and provides some helper methods.

    """

    def queue_message(self, subject='test', message='a test message',
                      from_email='sender@djangomailer',
                      recipient_list=None, priority=None):
        if recipient_list is None:
            recipient_list = ['recipient@djangomailer']
        email_message = mail.EmailMessage(subject, message, from_email,
                                          recipient_list)
        return queue_email_message(email_message, priority=priority)


def rfc_6532_support():
    """
    RFC 6532 is not properly supported in Django < 1.10 with Python 3.
    """
    django_version = django.get_version()
    return (six.PY2 or
            six.PY3 and StrictVersion(django_version) >= StrictVersion("1.10"))


RFC_6532_SUPPORT = rfc_6532_support()
