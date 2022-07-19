from unittest.mock import patch

from django.test import TestCase

from django_yubin.models import Message
from django_yubin.engine import send_db_message
from django_yubin.tasks import send_email, retry_emails, EnqueuedFailed


@patch('django_yubin.engine.send_db_message', side_effect=send_db_message)
class TestSendEmailTask(TestCase):

    def testSendEmailNotFound(self, send_db_message_mock):
        send_email(-1)
        self.assertFalse(send_db_message_mock.called)

    def testSendEmailSuccess(self, send_db_message_mock):
        message = Message.objects.create(
            to_address='johndoe@acmecorp.com',
            from_address='no-reply@acmecorp.com',
            subject='Lorem ipsum dolor sit amet',
            encoded_message='Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
        )
        send_email(message.pk)
        self.assertTrue(send_db_message_mock.called)
        message.refresh_from_db()
        self.assertEqual(message.status, Message.STATUS_SENT)


class TestRetryEmailsTask(TestCase):

    def testRetryEmailsEmpty(self):
        self.assertEqual(retry_emails(), EnqueuedFailed(0, 0))

    def testRetryEmailsNoRetrayable(self):
        Message.objects.create(
            to_address='',
            from_address='',
            subject='',
            encoded_message='',
        )
        self.assertEqual(retry_emails(), EnqueuedFailed(0, 0))

    def testRetryEmailsMaxRetries(self):
        retries = 2
        Message.objects.create(
            to_address='',
            from_address='',
            subject='',
            encoded_message='',
            status=Message.STATUS_FAILED,
            enqueued_count=retries + 1,
        )
        self.assertEqual(retry_emails(max_retries=retries), EnqueuedFailed(0, 0))

    def testRetryEmailsSuccess(self):
        emails_count = 2
        for i in range(emails_count):
            Message.objects.create(
                to_address='johndoe@acmecorp.com',
                from_address='no-reply@acmecorp.com',
                subject='Lorem ipsum dolor sit amet %s' % i,
                encoded_message='Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
                status=Message.STATUS_FAILED,
            )
        self.assertEqual(retry_emails(), EnqueuedFailed(emails_count, 0))

    @patch("django_yubin.tasks.send_email.delay", side_effect=Exception)
    def testRetryEmailsFailed(self, send_email_mock):
        Message.objects.create(
            to_address='johndoe@acmecorp.com',
            from_address='no-reply@acmecorp.com',
            subject='Lorem ipsum dolor sit amet',
            encoded_message='Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
            status=Message.STATUS_FAILED,
        )
        self.assertEqual(retry_emails(), EnqueuedFailed(0, 1))
