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

If this setting is ``True``, mail will not be sent when the ``send_mail``
command is called.


MAILER_USE_BACKEND
------------------
*Django 1.2 setting*

The mail backend to use when actually sending e-mail.
Defaults to ``'django.core.mail.backends.smtp.EmailBackend'``


MAILER_MAIL_ADMINS_PRIORITY
---------------------------
The default priority for messages sent via the ``mail_admins`` function of
Django Mailer 2.

The default value is ``constants.PRIORITY_HIGH``. Valid values are ``None``
or any of the priority from ``django_yubin.constants``:
``PRIORITY_EMAIL_NOW``, ``PRIORITY_HIGH``, ``PRIORITY_NORMAL`` or
``PRIORITY_LOW``.


MAILER_MAIL_MANAGERS_PRIORITY
-----------------------------
The default priority for messages sent via the ``mail_managers`` function of
Django Mailer 2.

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
