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

``FileStorageBackend`` uses `Django's default file storage <https://docs.djangoproject.com/en/3.2/ref/settings/#default-file-storage>`_ to save emails in the file system and only the path in the database.

With the help of `Django Storages <https://django-storages.readthedocs.io>`_ you can also save
emails in many other file/object storages: AWS S3, MinIO, Azure Storage, Google Cloud Storage, Dropbox,
SFTPs, etc.

Custom storage backends
-----------------------

If you have different needs, you can also write your own custom storage backend:

* Inherit from the base class ``django_yubin.storage_backends.BaseStorageBackend`` and implement its
  abstract methods for getting and settings the email.
* You can have a look at the other storage backends and the comments in ``django_yubin.models.Message``
  to have an idea.
* Set ``settings.MAILER_STORAGE_BACKEND`` with the path of your custom storage backend. For example,
  ``"my_project.storage_backends.MyCustomStorageBackend"``.

You can also inherit from other already implemented storage backends. For example, let's write a
custom storage backend that uses an inmutable file system storage:

.. code:: python

    # my_project.storage_backends.py

    from django.core.files.storage import FileSystemStorage
    from django_yubin.storage_backends import FileStorageBackend


    class _InmutableFileSystemStorage(FileSystemStorage):
        def delete(self, name):
            pass


    class InmutableFileStorageBackend(FileStorageBackend):
        storage = _InmutableFileSystemStorage()


.. code:: python

    # settings.py

    MAILER_STORAGE_BACKEND = 'my_project.storage_backends.InmutableFileStorageBackend'

Migrate between storage backends
--------------------------------

Yubin versions < 2.0.0 don't have storage backends and have all the emails saved in the database.
When you upgrade Yubin to a version >= 4.0.0, by default it uses the ``DatabaseStorageBackend`` so
you still have the emails in the database.

In case you want to use the ``FileStorageBackend``, Yubin provides a Django command to do the
migration moving emails from the database to the file storage. There is also the opposite command
if you want to use again the ``DatabaseStorageBackend``.

**Warning:** Consider to do a database and/or file storage backup before executing any of these
commads.

DB2File
^^^^^^^

* Stop any cron, Celery worker, etc. that can send emails.
* Change ``settings.MAILER_STORAGE_BACKEND`` to ``django_yubin.storage_backends.FileStorageBackend``.
* Execute::

    python manage.py db2file
* Enable again your Celery workers.


File2DB
^^^^^^^

* Stop any cron, Celery worker, etc. that can send emails.
* Change ``settings.MAILER_STORAGE_BACKEND`` to ``django_yubin.storage_backends.DatabaseStorageBackend``.
* Execute::

    python manage.py file2db
* Or if you also want to delete the files in the file storage after saving them into the database,
  execute::

    python manage.py file2db --delete
* Enable again your Celery workers.

If you use a different or custom storage backend and you want to migrate emails, you should write
your own migration commad.
