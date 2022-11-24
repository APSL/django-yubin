Storage backends
================

Yubin uses the database to save data about emails: dates, status (queued, sent...) and some fields
to easy access, filtering and searching without parsing the email.

In addition, it needs to save full email contents somewhere. Storage backends are responsible of
saving and retrieving these emails. You can choose one using the ``settings.MAILER_STORAGE_BACKEND``
variable.

DatabaseStorageBackend
----------------------

``django_yubin.storage_backends.DatabaseStorageBackend``

By default, Yubin saves emails in the database. This is a simple solution that works well if you
send few emails, they are text-only or you don't attach heavy files.

FileStorageBackend
------------------

``django_yubin.storage_backends.FileStorageBackend``

If that's not the case, the database can grow a lot with data that is read only a few times, it can
increase the size of your backup, etc.

This backend uses `Django's default file storage <https://docs.djangoproject.com/en/3.2/ref/settings/#default-file-storage>`_.

TODO: django storages - s3 minio

Migrate between backends
------------------------

DB2File
^^^^^^^

TODO

File2DB
^^^^^^^
TODO
