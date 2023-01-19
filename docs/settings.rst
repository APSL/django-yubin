Settings
========

List of settings that can be added to your Django project. All are optional and have sane defaults.


**MAILER_PAUSE_SEND**

Provides a way to temporarily pause sending mails. Default is ``False``.

If ``True``, mail will be discarded and not be sent by any function.


**MAILER_USE_BACKEND**

The mail backend to use when actually sending emails. Default is
``'django.core.mail.backends.smtp.EmailBackend'``.

*Tip*: You can use Django's console or dummy backends during development to avoid sending fake
emails.


**MAILER_TEST_MODE**

When ``True``, recipient addresses of all messages are replaced with the value of
``MAILER_TEST_EMAIL`` before being created and enqueued. An additional header
``X-Yubin-Test-Original`` will be added with the content of the original recipient addresses. Both
``MAILER_TEST_MODE`` and ``MAILER_TEST_EMAIL`` must evaluate to ``True`` to activate this mode.
Default is ``False``.


**MAILER_TEST_EMAIL**

Email address where all mail is sent when ``MAILER_TEST_MODE`` is ``True``. Default is ``''``.


**MAILER_HC_QUEUED_LIMIT_OLD**

If there are mails created or enqueued or in progress for more than ``MAILER_HC_QUEUED_LIMIT_OLD``
minutes, the HealthCheck view will show an error. Default is ``30`` minutes.


**MAILER_STORAGE_BACKEND**

Storage to save full emails. Default is ``django_yubin.storage_backends.DatabaseStorageBackend``.
You can also use ``django_yubin.storage_backends.FileStorageBackend`` or provide your own.


**MAILER_STORAGE_DELETE**

When deleting an email from the database, also delete its data from the storage.
Default is ``True``.


**MAILER_FILE_STORAGE_DIR**

Subdirectory to save emails when using the ``FileStorageBackend``. Default is ``yubin``.
