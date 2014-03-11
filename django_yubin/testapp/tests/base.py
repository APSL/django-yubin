#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from django.core import mail
from django.test import TestCase
from django_yubin import queue_email_message
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import backends

class FakeConnection(object):
    """
    A fake SMTP connection which diverts emails to the test buffer rather than
    sending.

    """
    def sendmail(self, *args, **kwargs):
        """
        Divert an email to the test buffer.

        """
        #FUTURE: the EmailMessage attributes could be found by introspecting
        # the encoded message.
        message = mail.EmailMessage('SUBJECT', 'BODY', 'FROM', ['TO'])
        mail.outbox.append(message)


class TestEmailBackend(BaseEmailBackend):
    '''
    An EmailBackend used in place of the default
    django.core.mail.backends.smtp.EmailBackend.

    '''
    def __init__(self, fail_silently=False, **kwargs):
        super(TestEmailBackend, self).__init__(fail_silently=fail_silently)
        self.connection = FakeConnection()

    def send_messages(self, email_messages):
        pass


class MailerTestCase(TestCase):
    """
    A base class for Django Mailer test cases which diverts emails to the test
    buffer and provides some helper methods.

    """
    #def setUp(self):
        #self.saved_email_backend = backends.smtp.EmailBackend
        #backends.smtp.EmailBackend = TestEmailBackend

    #def tearDown(self):
        #backends.smtp.EmailBackend = self.saved_email_backend

    def queue_message(self, subject='test', message='a test message',
                      from_email='sender@djangomailer',
                      recipient_list=['recipient@djangomailer'],
                      priority=None):
        email_message = mail.EmailMessage(subject, message, from_email,
                                          recipient_list)
        return queue_email_message(email_message, priority=priority)
