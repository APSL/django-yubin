import os
from abc import ABC, abstractmethod
from uuid import uuid4

from django.core.files.storage import default_storage

from . import settings


class BaseStorageBackend(ABC):
    @staticmethod
    @abstractmethod
    def get_encoded_message(message): pass

    @staticmethod
    @abstractmethod
    def set_encoded_message(message, value): pass


class DatabaseStorageBackend(BaseStorageBackend):
    @staticmethod
    def get_encoded_message(message):
        return message._encoded_message

    @staticmethod
    def set_encoded_message(message, value):
        message._encoded_message = value


class FileStorageBackend(BaseStorageBackend):
    @classmethod
    def get_encoded_message(cls, message):
        file = default_storage.open(cls.get_path(message), 'r')
        content = file.read()
        file.close()
        return content

    @classmethod
    def set_encoded_message(cls, message, value):
        path = cls.get_path(message)
        file = default_storage.open(path, 'w')
        file.write(value)
        file.close()
        message._encoded_message = path

    @staticmethod
    def get_path(message):
        return message._encoded_message or \
            os.path.join(settings.MAILER_FILE_STORAGE_DIR, f"{str(uuid4())}.msg")
