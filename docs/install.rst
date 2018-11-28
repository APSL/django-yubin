============
Installation
============

An obvious prerequisite of django-yubin is Django - 1.9 is the
minimum supported version.


Installing django_yubin
==========================

You can install the latest version from Pypi::

    pip install django-yubin


or you can download and install from sources http://github.com/APSL/django-yubin.git

If you're using pip__ and a virtual environment, this usually looks like::

    pip install -e git+http://github.com/APSL/django-yubin.git#egg=django-yubin

.. __: http://pip.openplans.org/

Or for a manual installation, once you've downloaded the package, unpack it
and run the ``setup.py`` installation script::

    python setup.py install


.. warning:: ``easy_install`` is untested and not recommended, especially if you
   mix it with pip. You might run into ``ImportError`` because the app
   cannot figure out which version is installed.


Configuring your project
========================

In your Django project's settings module, add django_yubin to your
``INSTALLED_APPS`` setting

.. code:: python

    INSTALLED_APPS = (
        ...
        'django_yubin',
    )



Note that django yubin doesn't implicitly queue all django mail (unless you
tell it to).

To queue all django mail you must configure the mail backend as

.. code:: python

    EMAIL_BACKEND = 'django_yubin.smtp_queue.EmailBackend'

More details can be found in the queue documentation.

Add *yubin* urls in your main *urls.py* for use the health check.

.. code:: python

    url(r'^yubin/', include('django_yubin.urls')),


Upgrading from previous versions
================================

Version 0.1.8 has added support for Django 1.9 and syncdb command no longer
exists. If you are upgrading from a version < 0.1.8 and your models are
already created you should execute::

    python manage.py migrate django_yubin --fake-initial


More details in https://docs.djangoproject.com/en/1.9/topics/migrations/#adding-migrations-to-apps
