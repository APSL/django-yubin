django-yubin
============

.. image:: https://github.com/APSL/django-yubin/actions/workflows/ci-cd.yml/badge.svg
  :target: https://github.com/APSL/django-yubin/actions/workflows/ci-cd.yml
  :alt: CI-CD status

.. image:: https://coveralls.io/repos/APSL/django-yubin/badge.svg
  :target: https://coveralls.io/r/APSL/django-yubin
  :alt: Coverage status

.. image:: https://img.shields.io/pypi/v/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin
  :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin
  :alt: Python versions

.. image:: https://img.shields.io/pypi/djversions/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin
  :alt: Django versions

.. image:: https://readthedocs.org/projects/django-yubin/badge/?version=latest
  :target: https://django-yubin.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation status


Django Yubin allows you to create, send and manage emails in your Django projects. It follows the
`12-factors app methodology <https://12factor.net/>`_.

Yubin means postal service in Japanese. Thanks `@morenosan <https://github.com/morenosan>`_ for the
name.

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
* Optionally you can save only minimum data in the database and full emails in a different storage.
* Yubin provides settings to avoid sending emails during development.


You can read the full documentation at http://django-yubin.readthedocs.org/
