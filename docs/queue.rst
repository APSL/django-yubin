=====
Usage
=====

django-yubin is asynchronous so in addition to putting mail on the queue you
need to periodically tell it to clear the queue and actually send the mail.

The latter is done via a command extension.


Putting Mail On The Queue
=================================================

In settings.py, configure Django's EMAIL_BACKEND setting like so:

.. code:: python

    EMAIL_BACKEND = 'django_yubin.smtp_queue.EmailBackend'

If you don't need message priority support you can call send_mail like
you normally would in Django

.. code:: python

    send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, recipients)

If you need prioritized messages, create an instance of EmailMessage
and specify ``{'X-Mail-Queue-Priority': '<value>'}`` in the ``headers`` parameter,
where <value> is one of:

    - 'now-not-queued' - do not queue, send immediately.
    - 'now' - send immediately.
    - 'high' - high priority.
    - 'normal' - standard priority - this is the default.
    - 'low' - low priority.

If you don't specify a priority, the message is sent at 'normal' priority.


Command Extensions
===================================

With mailer in your INSTALLED_APPS, there will be four new manage.py commands
you can run:

 - ``send_mail`` will clear the current message queue. If there are any
   failures, they will be marked deferred and will not be attempted again by
   ``send_mail``.

 - ``retry_deferred`` will move any deferred mail back into the normal queue
   (so it will be attempted again on the next ``send_mail``).

 - ``cleanup_mail`` will delete mails created before an X number of days
   (defaults to 90).

 - ``status_mail`` command allows systems like Nagios to able to check the queue status.
   It returns a string that can be parsed as (?P<queued>\d+)/(?P<deferred>\d+)/(?P<seconds>\d+).
   Adding ``--json-format option``, the output will be in JSON format.

 - ``send_test_mail`` send a simple email in order to check connection
   parameters.

 - ``create_email`` create fake mails for testing.

You may want to set these up via cron to run regularly::

    * * * * * (cd $PROJECT; python manage.py send_mail >> $PROJECT/cron_mail.log 2>&1)
    0,20,40 * * * * (cd $PROJECT; python manage.py retry_deferred >> $PROJECT/cron_mail_deferred.log 2>&1)
    0 1 * * * (cd $PROJECT; python manage.py cleanup_mail --days=30 >> $PROJECT/cron_mail_cleanup.log 2>&1)

This attempts to send mail every minute with a retry on failure every 20 minutes
and will run a cleanup task every day cleaning all the messaged created before
30 days.

``manage.py send_mail`` uses a lock file in case clearing the queue takes
longer than the interval between calling ``manage.py send_mail``.

Note that if your project lives inside a virtualenv, you also have to execute
this command from the virtualenv. The same, naturally, applies also if you're
executing it with cron.

Health Check
============

Go to ``http://yourproject/yubin/health`` for see the health output result. You can see shomething like that:

.. code:: text

    oldest_queued_email: 1 mins
    emails_queued_too_old: no

or...

.. code:: text

    oldest_queued_email: 45 mins
    emails_queued_too_old: yes

You can use this view's response in your check system.

