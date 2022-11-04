import os
from abc import ABC, abstractmethod
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from . import settings


class BaseStorageBackend(ABC):
    @classmethod
    @abstractmethod
    def get_encoded_message(cls, message): pass

    @classmethod
    @abstractmethod
    def set_encoded_message(cls, message, value): pass

    @classmethod
    def admin_display_encoded_message(cls, model_admin, message):
        return f'''
            <textarea class="vLargeTextField" cols="40" rows="15" style="width: 99%;" disabled
            readonly>{message.encoded_message}</textarea>
        '''.strip()


class DatabaseStorageBackend(BaseStorageBackend):
    @classmethod
    def get_encoded_message(cls, message):
        return message._encoded_message

    @classmethod
    def set_encoded_message(cls, message, value):
        message._encoded_message = value


class FileStorageBackend(BaseStorageBackend):
    @classmethod
    def get_encoded_message(cls, message):
        file = default_storage.open(cls.get_path(message), 'rb')
        content = file.read().decode('utf-8')
        file.close()
        return content

    @classmethod
    def set_encoded_message(cls, message, value):
        path = cls.get_path(message)
        new_path = default_storage.save(path, ContentFile(value.encode('utf-8')))
        if message._encoded_message:
            default_storage.delete(message._encoded_message)
        message._encoded_message = new_path

    @staticmethod
    def get_path(message):
        return message._encoded_message or \
            os.path.join(settings.MAILER_FILE_STORAGE_DIR, f"{str(uuid4())}.msg")

    @classmethod
    def admin_display_encoded_message(cls, model_admin, message):
        return f'''
            <div>
                <a href="{default_storage.url(message._encoded_message)}">
                    {message._encoded_message}
                </a>
            </div>
            <br>
            {super(cls, cls).admin_display_encoded_message(model_admin, message)}
        '''.strip()
