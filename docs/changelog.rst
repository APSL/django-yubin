Changelog
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Starting from version 2.0.0, the format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_.

[2.0.5] - 2024-06-21
--------------------

Fixed
^^^^^
* Use ``BigAutoField`` and migrate all existing auto fields to it. This avoids generating a new migration in projects that use ``settings.DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"``.

[2.0.4] - 2024-05-02
--------------------

Changed
^^^^^^^
* <6 upper bound to celery dependency.

[2.0.3] - 2024-01-09
--------------------

Fixed
^^^^^
* Fix race condition between Celery and database transactions (https://github.com/APSL/django-yubin/pull/74)

[2.0.2] - 2023-10-30
--------------------

Changed
^^^^^^^
* Improve performance of data migration when migrating from versions < 2.0 (https://github.com/APSL/django-yubin/pull/69)

Fixed
^^^^^
* Perform unfolding of headers when parsing messages (https://github.com/APSL/django-yubin/pull/71)

[2.0.1] - 2023-08-10
--------------------

Changed
^^^^^^^
* Ensure parsed e-mail message doesn't discard information (https://github.com/APSL/django-yubin/pull/67)

[2.0.0] - 2023-06-29
--------------------

Changed
^^^^^^^
* Send and queue emails with Celery instead of with Cron.
* Drop priority headers (useless with queues).
* Storage backends to save emails in databases, file storages, etc.
* Cc and Bcc support.
* Supported versions: Python 3.8~3.11, Django 3.2~4.2, Celery 5.0~5.2.
* Migrate CI/CD from Travis to Github Actions.
* Docker Compose for external dependencies in development environment.
* Get django_yubin version programmatically.
* Update docs.


Older versions - 2022-01-17
---------------------------

* 1.7.1 - Remove abandoned ``pyzmail36`` dependency with ``mail-parser``.
* 1.7.0 - Add optional ``MAILER_MESSAGE_SEARCH_FIELDS`` setting. It's a tuple of strings with the fields to use in ``admin.Message.search_fields`` attribute.
* 1.6.0 - Support for Django 3.0
* 1.5.0 - New TemplatedMultipleAttachmentsEmailMessageView to allow to send emails with more than 1 attachment.
* 1.4.1 - Detecting if messages are encoding using different encoding headers to be able to preview them (now base64, quoted-printable).
* 1.4.0 - Option added in status_mail command to return the output in json format.
* 1.3.1 - Fix unicode and encode errors: sending queued and non queued emails and in admin detail view.
* 1.3.0 - Allow to send emails inmediatly without being saved in database (priority «now-not-queued»). Add support for Python 3.7 and Django 2.1. Remove old code for Django < 1.3.
* 1.2.0 - Fix is_base64 detection. Add a «send_test_email» command to check connection parameters. New health check view. Don't open a connection if there are no messages in queue to send. Add a "date_sent" field to detect when the mail was sent.
* 1.1.0 - Fix attachment headers in TemplateAttachmentEmailMessagView making both "attachment" and "filename" args mandatory.
* 1.0.5 - Add missing paths in MANIFEST.in.
* 1.0.4 - Fix attachment visualization in the admin. Attach pdf in create_mail command. Solved Content-Transfer-Encoding issue.
* 1.0.3 - Fixed issue decoding the message payload, added support for django 1.9, updated changelog and added support to deploy the package from travis.
* 1.0.0 - Add support for Django 2.0 and remove django 1.8.
* 0.8.2 - Fix date created column in QueuedMessages admin.
* 0.8.1 - Ensure that LOCK_WAIT_TIMEOUT is never negative to avoid a bug in lockfile in systems which use a LinkFileLock.
* 0.8.0 - Use settings.MAILER_PAUSE_SEND to skip smtp connections. Fix UTF-8 encoding in messages. Fix encoding errors in email visualization in the admin.
* 0.7.0 - Fix template context bug for Django 1.11. Add Python 3.6 to CI and drop Python 3.3 and Django 1.9.
* 0.6.0 - Support for Python 3.6.
* 0.5.0 - Limit nº of emails sent by send_mail command. Update the debug handlers options for verbosity to accept v3.
* 0.4.0 - Support Django 1.11: subject and body are no longer unscaped, you need to add {% autoescape off %} to your non HTML templates.
* 0.3.1 - Delete unused template that caused an error with django-compressor offline. testmail command now generates HTML emails.
* 0.3.0 - Support Django >= 1.8 and <=1.10, Python 2.7, 3.3, 3.4 and 3.5. Re-send mails admin action. Fix bug in status_mail command. Demo project configured to send mails with the same mail fake-server used for tests.
* 0.2.3 - Removed {% load url from future %} to support Django 1.9. Now Django < 1.5 is not supported.
* 0.2.2 - Include migrations directory in .tar.gz in PyPi.
* 0.2.1 - Updated links to CI and Code Coverage Services
* 0.2.0 - Merged  sergei-maertens contribution.
* 0.1.8 - Added migrations for Django 1.9 compatibility. See http://django-yubin.readthedocs.org/en/latest/install.html#upgrading-from-previous-versions
* 0.1.7 - Support for Django 1.8.
* 0.1.6 - Bugfixes.
* 0.1.5 - Bugfixes.
* 0.1.4 - Updated README.
* 0.1.3 - Fixed Python3 compatibility, thanks Marc, Cesc & Dani.
* 0.1.2 - Fixed Templates.
* 0.1.1 - Updated documentation and unit tests.
