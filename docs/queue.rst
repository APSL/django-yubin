Enqueue and send
================

Putting emails in the queue
---------------------------

Yubin replaces the standard Django Email Backend with its own. Instead of sending emails
synchronously trough a SMTP server, Yubin saves and equeues emails in your database and creates
Celery tasks to send them asynchronously using "the real" Django Email Backend.

.. code:: python

    # settings.py

    # Yubin email backend that enqueue emails
    EMAIL_BACKEND = 'django_yubin.backends.QueuedEmailBackend'

    # "The real" email backend for sending emails
    MAILER_USE_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

Now, you can call ``send_mail`` like you normally do in Django or using
:doc:`mail views <mailviews>`

.. code:: python

    send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, recipients)
    # ...
    WelcomeMessageView(user).send()

Tasks
-----

Once you have your emails queued in the database, you can send, retry or delete them using the
following Celery tasks:

- **send_email(message_pk)** Sends the email from the database with the given primay key.
- **retry_emails(max_retries=3)** Retry sending retryable emails (failed, blacklisted or discarded)
  enqueueing them again.
- **delete_old_emails(days=90)** Delete emails created before `days` days.

You don't usually need to create a ``send_email`` task, Yubin email backend does it automatically. For ``retry_emails`` and ``delete_old_emails``, you can use `Celery Beat <https://django-celery-beat.readthedocs.io/en/latest/>`_ to schedule periodic task.

Remember to have at least one `Celery worker <https://django-celery-beat.readthedocs.io/en/latest/#example-running-periodic-tasks>`_ listening for tasks.

Commands
--------

In addition to tasks, Yubin also provides a couple of commands to facilitate the development:

- **send_test_mail** Sends a single HTML email. Ideal for checking connection parameters.
- **create_email** Creates fake mails for testing unicode, emojis and attachments.
- **db2file** and **file2db** migrate emails between storage backends. Look at the
  :doc:`Storage backends <storages>` section for more details.

Execute ``python manage.py THE_COMMAND --help`` to see optional arguments.

Health check
------------

If you have added ``url(r'^yubin/', include('django_yubin.urls'))`` to your ``urls.py``, you can go
to ``http://localhost:8000/yubin/health`` and see the health output result.

Response when there are no problems: HTTP 200

.. code:: text

    oldest_queued_email: 1 mins
    emails_queued_too_old: no
    threshold: 30 mins

Response if there are emails that have been too long enqueued: HTTP 500

.. code:: text

    # HTTP 500
    oldest_queued_email: 45 mins
    emails_queued_too_old: yes
    threshold: 30 mins

You can parse this view's response in your check system and check the status code of the response.

Additionally, you can use a different threshold changing ``settings.MAILER_HC_QUEUED_LIMIT_OLD`` or
passing a GET parameter `t`: http://localhost:8000/yubin/health?t=60
