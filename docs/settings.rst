========
Settings
========

Following is a list of settings which can be added to your Django settings
configuration. All settings are optional and the default value is listed for
each.


MAILER_PAUSE_SEND
-----------------

Provides a way of temporarily pausing the sending of mail. Defaults to
``False``.

If this setting is ``True``, mail will not be sent by any function.


MAILER_USE_BACKEND
------------------

*Django 1.2 setting*

The mail backend to use when actually sending e-mail.
Defaults to ``'django.core.mail.backends.smtp.EmailBackend'``


MAILER_MAIL_ADMINS_PRIORITY
---------------------------

The default priority for messages sent via the ``mail_admins`` function of
Django Yubin.

The default value is ``constants.PRIORITY_HIGH``. Valid values are ``None``
or any of the priority from ``django_yubin.constants``:
``PRIORITY_NOW_NOT_QUEUED``, ``PRIORITY_NOW``, ``PRIORITY_HIGH``,
``PRIORITY_NORMAL`` or ``PRIORITY_LOW``.


MAILER_MAIL_MANAGERS_PRIORITY
-----------------------------

The default priority for messages sent via the ``mail_managers`` function of
Django Yubin.

The default value is ``None``. Valid values are the same as for
`MAILER_MAIL_ADMINS_PRIORITY`_.


MAILER_EMPTY_QUEUE_SLEEP
------------------------

For use with the ``django_yubin.engine.send_loop`` helper function.

When queue is empty, this setting controls how long to wait (in seconds)
before checking again. Defaults to ``30``.


MAILER_LOCK_WAIT_TIMEOUT
------------------------

A lock is set while the ``send_mail`` command is being run. This controls the
maximum number of seconds the command should wait if a lock is already in
place.

The default value is ``-1`` which means to never wait for the lock to be
available.

MAILER_TEST_MODE
----------------

When MAILER_TEST_MODE is ``True``, recipient addresses of all sent messages are replaced with
the value of the MAILER_TEST_EMAIL setting, before being sent.
An additional header ``X-Yubin-Test-Original`` will be inserted, with the content of the original
recipient addresses.

Both, MAILER_TEST_MODE and MAILER_TEST_EMAIL, must evaluate to ``True`` to activate this mode.

Defaults to ``False``.

MAILER_TEST_EMAIL
-------------------------

String with the email where all email are sent When MAILER_TEST_MODE is on.

Defaults to ``''``.


MAILER_HC_QUEUED_LIMIT_OLD
--------------------------

String to define the max minutes for the message health check. If there exists an old messages in the email's queue the health check will warn.

Defaults to: ``30``


MAILER_MESSAGE_SEARCH_FIELDS
----------------------------

Tuple of strings with the fields to use in ``admin.Message.search_fields`` attribute.

Defaults to all the text fields: ``('to_address', 'subject', 'from_address', 'encoded_message')``
