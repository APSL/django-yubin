=====
Usage
=====

django-yubin is asynchronous so in addition to putting mail on the queue you
need to periodically tell it to clear the queue and actually send the mail.

The latter is done via a command extension.


Putting Mail On The Queue (Django 1.3 or higher)
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

    - 'now' - do not queue, send immediately
    - 'high' - high priority
    - 'normal' - standard priority - this is the default.
    - 'low' - low priority

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

 - ``status_mail`` the intent of this commant is to allow systems as nagios to
    be able to ask the queue about its status. It returns as string with than
    can be parses as ``(?P<queued>\d+)/(?P<deferred>\d+)/(?P<seconds>\d+)``

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
