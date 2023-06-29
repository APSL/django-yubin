Installation
============

An obvious prerequisite of django-yubin is Django.

Installing Django Yubin
-----------------------

You can install the latest stable version from PyPI::

    pip install django-yubin

or the latest commit from `Github <https://github.com/APSL/django-yubin>`_::

    pip install -e git+http://github.com/APSL/django-yubin.git#egg=django-yubin

You can also download and install it manual with the ``setup.py`` installation script::

    python setup.py install

Configuring your project
------------------------

In your Django project's settings module, add ``django_yubin`` to your ``INSTALLED_APPS`` setting

.. code:: python

    INSTALLED_APPS = (
        ...
        'django_yubin',
    )

Note that yubin doesn't queue all email by default, you must configure the email backend as

.. code:: python

    EMAIL_BACKEND = 'django_yubin.backends.QueuedEmailBackend'
    MAILER_USE_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

More Yubin settings can be found in the :doc:`Settings sections <settings>`.

Add ``yubin`` urls in your main ``urls.py`` for using the health check

.. code:: python

    url(r'^yubin/', include('django_yubin.urls')),

Also, you need to setup `Celery <https://docs.celeryq.dev/en/stable/>`_ in your
`Django project <https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html>`_ and have
at least one worker listening to the queue.

Finally, run database migrations

.. code:: python

    python manage.py migrate

With this setup emails will be saved entirely in the database. You can also configure Yubin to save
emails in a different :doc:`storage <storages>`.

Upgrading from previous versions
--------------------------------

**Upgrading from versions < 0.1.8 to < 2.0.0**

Version 0.1.8 added support for Django 1.9 and syncdb command no longer exists. If you are
upgrading from a version < 0.1.8 and your models are already created you should execute

.. code:: bash

    $ python manage.py migrate django_yubin --fake-initial

More details in https://docs.djangoproject.com/en/4.1/topics/migrations/#adding-migrations-to-apps


**Upgrading from versions >= 0.1.8 to >= 2.0.0**

Version 2.0.0 is a big reimplementation that uses Celery tasks instead of Cron jobs. This change
needed considerable database schema changes but the database migrations take care of all. Keep
in mind that:

* These database schema changes can not be undone. Once you migrate to version >= 2 you can not go
  backwards and use again a version < 2 unless you have a previous database backup.
* Stop cron jobs before doing the migration to avoid sending emails in an undetermined migration
  state.
* Have Celery setup and configuration ready but with no workers running. One of the migrations
  generates tasks to enqueue emails that were enqueued so they will be sent later.
* Once the migration finishes and everything is OK, start Celery workers so enqueued emails will
  be sent.
