import logging
import os
from abc import ABC, abstractmethod
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string

from . import settings as yubin_settings
from .models import Message


logger = logging.getLogger(__name__)


class StorageBackendException(Exception):
    pass


class BaseStorageBackend(ABC):
    @classmethod
    @abstractmethod
    def get_message_data(cls, message): pass

    @classmethod
    @abstractmethod
    def set_message_data(cls, message, data): pass

    @classmethod
    @abstractmethod
    def delete_message_data(cls, message): pass

    @classmethod
    def admin_display_message_data(cls, model_admin, message):
        return f'''
            <textarea class="vLargeTextField" cols="40" rows="15" style="width: 99%;" disabled
            readonly>{message.message_data}</textarea>
        '''.strip()


class DatabaseStorageBackend(BaseStorageBackend):
    @classmethod
    def get_message_data(cls, message):
        return message._message_data

    @classmethod
    def set_message_data(cls, message, data):
        message._message_data = data

    @classmethod
    def delete_message_data(cls, message):
        pass


class FileStorageBackend(BaseStorageBackend):
    storage = default_storage

    @classmethod
    def get_message_data(cls, message):
        file = cls.storage.open(cls.get_path(message), 'rb')
        content = file.read().decode(settings.DEFAULT_CHARSET)
        file.close()
        return content

    @classmethod
    def set_message_data(cls, message, data):
        path = cls.get_path(message)
        new_path = cls.storage.save(path, ContentFile(data.encode(settings.DEFAULT_CHARSET)))
        if message._message_data:
            cls.storage.delete(message._message_data)
        message._message_data = new_path

    @staticmethod
    def get_path(message):
        return message._message_data or \
            os.path.join(yubin_settings.MAILER_FILE_STORAGE_DIR, f"{str(uuid4())}.msg")

    @classmethod
    def delete_message_data(cls, message):
        cls.storage.delete(cls.get_path(message))

    @classmethod
    def admin_display_message_data(cls, model_admin, message):
        return f'''
            <div>
                <a href="{cls.storage.url(message._message_data)}">
                    {message._message_data}
                </a>
            </div>
            <br>
            {BaseStorageBackend.admin_display_message_data(model_admin, message)}
        '''.strip()


def db2file():
    """
    Migrate emails from DatabaseStorageBackend to FileStorageBackend.
    """
    backend = import_string(yubin_settings.MAILER_STORAGE_BACKEND)
    if backend != FileStorageBackend:
        raise StorageBackendException(
            f'settings.MAILER_STORAGE_BACKEND should be {FileStorageBackend} instead of {backend}')

    messages = Message.objects \
        .filter(storage='django_yubin.storage_backends.DatabaseStorageBackend') \
        .only('pk', '_message_data', 'storage')
    for message in messages:
        db_message_data = DatabaseStorageBackend.get_message_data(message)
        DatabaseStorageBackend.set_message_data(message, data='')
        message.storage = yubin_settings.MAILER_STORAGE_BACKEND
        message.message_data = db_message_data
        message.save()
        logger.info(f'Message {message.pk} migrated. Saved in {message._message_data}')


def file2db(delete=False):
    """
    Migrate emails from FileStorageBackend to DatabaseStorageBackend optionally deleting the files
    from the file storage.
    """
    backend = import_string(yubin_settings.MAILER_STORAGE_BACKEND)
    if backend != DatabaseStorageBackend:
        raise StorageBackendException(
            f'settings.MAILER_STORAGE_BACKEND should be {DatabaseStorageBackend} instead of {backend}')

    messages = Message.objects \
        .filter(storage='django_yubin.storage_backends.FileStorageBackend') \
        .only('pk', '_message_data', 'storage')
    for message in messages:
        file_message_path = FileStorageBackend.get_path(message)
        file_message_data = FileStorageBackend.get_message_data(message)
        message.storage = yubin_settings.MAILER_STORAGE_BACKEND
        message.message_data = file_message_data
        message.save()
        logger.info(f'Message {message.pk} migrated')

        if delete:
            FileStorageBackend.storage.delete(file_message_path)
            logger.info(f'File {file_message_path} deleted from FileStorageBackend')
