from six import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .base import MessageMixin


class TestCommands(MessageMixin, TestCase):
    """
    A test case for Django management commands.
    """
    def test_create_mail(self):
        """
        The ``create_mail`` command create new mails.
        """
        out = StringIO()
        quantity = 2
        call_command('create_mail', quantity=quantity, stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(quantity, created)

    def test_send_test_mail(self):
        """
        The ``send_test_mail`` sends a test mail to test connection params
        """
        out = StringIO()
        call_command('send_test_mail', to='test@test.com', stdout=out)
        created = int(out.getvalue().split(':')[1])
        self.assertEqual(1, created)

    def test_send_test_no_email(self):
        """
        The ``send_test_mail`` without to email. Expect an error.
        """
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass

    def test_send_test_no_admins(self):
        """
        The ``send_test_mail`` without to email. Expect an error.
        """
        settings.ADMINS = []
        try:
            call_command('send_test_mail')
            self.fail("Should fail without to address")
        except CommandError:
            pass
