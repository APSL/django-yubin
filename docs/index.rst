Django Yubin
============

Django Yubin allows you to create, send and manage emails in your Django projects. It follows the
`12-factors app methodology <https://12factor.net/>`_.

How it works
------------

For creating and composing emails, Yubin provides class-based views that use standard Django
templates.

For sending and queuing emails, Yubin replaces the standard Django Email Backend with its own.
Instead of sending emails synchronously trough a SMTP server, Yubin saves emails in your database
(and optionally in a file storage) and sends them asynchronously using the
`Celery <https://docs.celeryq.dev/en/stable/>`_ distributed task queue.

Advantages
----------

* Create and compose emails reusing your code easily with class-based views.
* Your app can respond requests faster because other process/worker is managing the connection with
  the SMTP server for sending emails.
* Scale out easily adding more Celery workers.
* Emails are saved in the database, you can see, manage and enqueue them from the Django Admin.
* Yubin provides settings to avoid sending emails during development.

It's a fork!
------------

Yubin was forked from a django-mailer-2 fork which is a fork form Chris Beaven's fork of James
Tauber's `django-mailer <https://github.com/pinax/django-mailer>`_.

History
^^^^^^^

Chris Beaven started a fork of django-mailer and it got to the point when it would be rather
difficult to merge back. The fork was then renamed to the completely unimaginative
"django mailer 2".

At `APSL <https://github.com/APSL/>`_, we were always using this project together with
`mailviews <https://github.com/disqus/django-mailviews>`_, so we joined both together and started
to add our own features.

Differences
^^^^^^^^^^^

Some of the larger differences in django yubin:

* It's integrated with django-mailviews classes.
* It saves a rendered version of the email, so HTML and other attachments are handled fine.
* This rendered emails can be saved in diferent sotrages: database, file system, AWS S3 or even
  your own custom storage.
* Models have been completely refactored for a better logical separation of data.
* Provides replacements for ``send_mail``, ``mail_admins`` and ``mail_managers`` Django functions.
* Uses Celery distributed task queue instead of Cron.
* Task to remove old emails so the database does not increase so much.
* Improved admin configuration.
* Added a demo project for development and to see it in action in the admin.
* Support for runing tests without having to install and configure a Django application.
* Added CI and code coverage.
* Added a health check view.

Credit
------

At the time of the fork, the primary authors of django-mailer were James Tauber and Brian Rosner.
Additional contributors include Michael Trier, Doug Napoleone and Jannis Leidel.

Original branch and the django-mailer-2 hard work comes from Chris Beaven.

django-mailviews from Disqus.

The name "Yubin" was suggested by `@morenosan <https://github.com/morenosan>`_, he says it means
"postal mail" in Japanesse, but who knows! :)

For Yubin contributors, have a look at
`Github's contributor's list <https://github.com/APSL/django-yubin/graphs/contributors>`_ and
`humans.txt <https://github.com/APSL/django-yubin/blob/master/humans.txt>`_.

Index
-----

.. toctree::
    :maxdepth: 2

    install
    mailviews
    queue
    storages
    settings
    contributing
    changelog
