django-yubin
============

.. image:: https://travis-ci.org/APSL/django-yubin.svg
    :target: https://travis-ci.org/APSL/django-yubin

.. image:: https://codecov.io/github/APSL/django-yubin/coverage.svg?branch=master
    :target: https://codecov.io/github/APSL/django-yubin?branch=master

.. image:: https://coveralls.io/repos/APSL/django-yubin/badge.svg
  :target: https://coveralls.io/r/APSL/django-yubin

.. image:: https://img.shields.io/pypi/v/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin

.. image:: https://img.shields.io/pypi/pyversions/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin

.. image:: https://img.shields.io/pypi/djversions/django-yubin.svg
  :target: https://pypi.python.org/pypi/django-yubin

.. image:: https://readthedocs.org/projects/django-yubin/badge/?version=latest
  :target: http://django-yubin.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status

Django Yubin allows the programmer to control when he wants to send the e-mail
in this application, making the web application to answer fast as it not has to
wait for the mail server.

As in our projects we use always two django packages for dealing with emails:
django-mailer2 (our own fork in APSL) and django-mailviews to compose the
emails we decided to create this package to fit our own needs and share with
the community.

As you can see it seems django-mailer2 is not accepting patches, so in
order to put a new version on pypi a new name was mandatory.  So django-yubin was born
(yubin is postal mail in japanese). The name attribution is for @morenosan.

How it works
------------

Yubin replaces the standard Django Email Backend with its own. Instead of sending
the e-mail trough the SMTP server Yubin stores the e-mails on the database and
allows you to sent them using a cron command.

Advantages
~~~~~~~~~~

* Your application can answer faster, as other process is going to take care of
  connecting with the SMTP server and sending the e-mail.

* Yubin stores the e-mail and allows you to retrieve using the admin. Even with
  the attachments.

* Yubin allows to define prioritary queues, resend e-mails

* Yubin helps in your development.  It's a good way to work when you're developing
  the application and you don't want to flood your test users with
  e-mails. With Django Yubin, and without running the cron commands, you can see how
  your e-mails are, retrieve them and even delete them with out sending it.

On production mode you'll just nedd to add a cron entry in your server to send the e-mails,
someting like

    * * * * * (cd $PROJECT; python manage.py send_mail >> $PROJECT/cron_mail.log 2>&1)

This will send the queued e-mail every minute.

Django Yubin is a fork from django-mailer2 with some additions from django-mailviews and
additional improvements made from apsl.net that we need for our daly basis workd. It
has also contributions from other people, so don't heasitate to read the humans.txt.

django-mailer-2 by is a Chris Beaven fork from a fork of
James Tauber's django-mailer and is a reusable Django app for queuing the sending of email.

django-mailviews from Disqus, allows you to compose e-mails using templates in
the same way you compose your html templates, and allows you to preview the
e-mails.

If you want to run the test you'll need a test smtpd server, you can find one in

    ./bin/fake-server

run it in a different console and execute `runtests.py`

You can read the package documentation at http://django-yubin.readthedocs.org/en/latest/

Changelog
---------
* 1.7.1       Remove abandoned ``pyzmail36`` dependency with ``mail-parser``.
* 1.7.0       Add optional ``MAILER_MESSAGE_SEARCH_FIELDS`` setting. It's a tuple of strings with the fields to use in ``admin.Message.search_fields`` attribute.
* 1.6.0       Support for Django 3.0
* 1.5.0       New TemplatedMultipleAttachmentsEmailMessageView to allow to send emails with more than 1 attachment.
* 1.4.1       Detecting if messages are encoding using different encoding headers to be able to preview them (now base64, quoted-printable).
* 1.4.0       Option added in status_mail command to return the output in json format.
* 1.3.1       Fix unicode and encode errors: sending queued and non queued emails and in admin detail view.
* 1.3.0       Allow to send emails immediately without being saved in database (priority «now-not-queued»). Add support for Python 3.7 and Django 2.1. Remove old code for Django < 1.3.
* 1.2.0       Fix is_base64 detection. Add a «send_test_email» command to check connection parameters. New health check view. Don't open a connection if there are no messages in queue to send. Add a "date_sent" field to detect when the mail was sent.
* 1.1.0       Fix attachment headers in TemplateAttachmentEmailMessagView making both "attachment" and "filename" args mandatory.
* 1.0.5       Add missing paths in MANIFEST.in.
* 1.0.4       Fix attachment visualization in the admin. Attach pdf in create_mail command. Solved Content-Transfer-Encoding issue.
* 1.0.3       Fixed issue decoding the message payload, added support for django 1.9, updated changelog and added support to deploy the package from travis.
* 1.0.0       Add support for Django 2.0 and remove django 1.8.
* 0.8.2       Fix date created column in QueuedMessages admin.
* 0.8.1       Ensure that LOCK_WAIT_TIMEOUT is never negative to avoid a bug in lockfile in systems which use a LinkFileLock.
* 0.8.0       Use settings.MAILER_PAUSE_SEND to skip smtp connections. Fix UTF-8 encoding in messages. Fix encoding errors in email visualization in the admin.
* 0.7.0       Fix template context bug for Django 1.11. Add Python 3.6 to CI and drop Python 3.3 and Django 1.9.
* 0.6.0       Support for Python 3.6.
* 0.5.0       Limit nº of emails sent by send_mail command. Update the debug handlers options for verbosity to accept v3.
* 0.4.0       Support Django 1.11: subject and body are no longer unscaped, you need to add {% autoescape off %} to your non HTML templates.
* 0.3.1       Delete unused template that caused an error with django-compressor offline. testmail command now generates HTML emails.
* 0.3.0       Support Django >= 1.8 and <=1.10, Python 2.7, 3.3, 3.4 and 3.5. Re-send mails admin action. Fix bug in status_mail command. Demo project configured to send mails with the same mail fake-server used for tests.
* 0.2.3       Removed {% load url from future %} to support Django 1.9. Now Django < 1.5 is not supported.
* 0.2.2       Include migrations directory in .tar.gz in PyPi.
* 0.2.1       Updated links to CI and Code Coverage Services
* 0.2.0       Merged  sergei-maertens contribution.
* 0.1.8       Added migrations for Django 1.9 compatibility. See http://django-yubin.readthedocs.org/en/latest/install.html#upgrading-from-previous-versions
* 0.1.7       Support for Django 1.8.
* 0.1.6       Bugfixes.
* 0.1.5       Bugfixes.
* 0.1.4       Updated README.
* 0.1.3       Fixed Python3 compatibility, thanks Marc, Cesc & Dani.
* 0.1.2       Fixed Templates.
* 0.1.1       Updated documentation and unit tests.

