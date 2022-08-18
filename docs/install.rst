Installation
============

An obvious prerequisite of django-yubin is Django.

Installing django_yubin
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

More yubin settings can be found in the :doc:`Settings sections <settings>`.

Also, you need to setup `Celery <https://docs.celeryq.dev/en/stable/>`_ in your
`Django project <https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html>`_.

Add ``yubin`` urls in your main ``urls.py`` for using the health check

.. code:: python

    url(r'^yubin/', include('django_yubin.urls')),

Finally, run database migrations

.. code:: python

    python manage.py migrate django_yubin

Upgrading from previous versions
--------------------------------

Version 0.1.8 added support for Django 1.9 and syncdb command no longer exists. If you are
upgrading from a version < 0.1.8 and your models are already created you should execute::

    python manage.py migrate django_yubin --fake-initial

More details in https://docs.djangoproject.com/en/1.9/topics/migrations/#adding-migrations-to-apps


Version 2.0.0 TODO...
