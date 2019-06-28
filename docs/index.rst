===============
django_yubin
===============

Django Yubin is used to queue e-mails. This allows the emails to be sent
asynchronously (by the use of a command extension) rather than blocking the
response.

It also provides with some classes that allows you to compose e-mails in the same way you compose your django
templates, using different templates for subject, body and html content.

Index
=====

.. toctree::

    install
    queue
    mailviews
    settings
    contributing


It's a fork!
=============

Yes, it's a fork, fork, comes from django-mailer-2 fork which is a fork form Chris Beaven fork to of James Tauber's
`django-mailer`__

This document is readthedocs version of the fork that Chris and James made
the original document with some additional information.

.. __: http://github.com/jtauber/django-mailer

History
-------

Chris Beaven started a fork of django-mailer and it got to the point when it
would be rather difficult to merge back. The fork was then renamed to the
completely unimaginative "django mailer 2".

As always found myself using this project with the mailviews__ classes, we
adapted some of the mailviews to add priority and some convenience classes.

.. __: https://github.com/disqus/django-mailviews


Differences
-----------

Some of the larger differences in django_yubin:

* Needs Django 1.9+

* It saves a rendered version of the email instead - so HTML and other
  attachments are handled fine

* The models were completely refactored for a better logical separation of
  data.

* It provides a hook to override (aka "monkey patch") the Django ``send_mail``,
  ``mail_admins`` and ``mail_manager`` functions.

* Added a management command to remove old e-mails, so the database does not
  increase so much.

* Added a new testing procedure, so you can run the tests without having to
  install and configure a Django application.

* Added some cron templates ein `bin` folder to help you to configure the
  cron.

* Improved admin configuration.

* Added a demo project, which shows how we can retrieve an email stored in
  the database and shows django-mailer in the admin.

* Integrated django-mailviews classes

* Added to CI and code coverage.

Credit
------

At the time of the fork, the primary authors of django-mailer were James Tauber
and Brian Rosner. The additional contributors included Michael Trier, Doug
Napoleone and Jannis Leidel.

Original branch and the django-mailer-2 hard work comes from Chris Beaven.

django-mailviews from Disqus

The name django-yubin was suggested by @morenosan, he says it means "postal mail" in japanesse, but who knows! :)


