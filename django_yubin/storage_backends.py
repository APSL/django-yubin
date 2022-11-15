import os
from abc import ABC, abstractmethod
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from . import settings as yubin_settings


class BaseStorageBackend(ABC):
    @classmethod
    @abstractmethod
    def get_message_data(cls, message): pass

    @classmethod
    @abstractmethod
    def set_message_data(cls, message, data): pass

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


class FileStorageBackend(BaseStorageBackend):
    @classmethod
    def get_message_data(cls, message):
        file = default_storage.open(cls.get_path(message), 'rb')
        content = file.read().decode(settings.DEFAULT_CHARSET)
        file.close()
        return content

    @classmethod
    def set_message_data(cls, message, data):
        path = cls.get_path(message)
        new_path = default_storage.save(path, ContentFile(data.encode(settings.DEFAULT_CHARSET)))
        if message._message_data:
            default_storage.delete(message._message_data)
        message._message_data = new_path

    @staticmethod
    def get_path(message):
        return message._message_data or \
            os.path.join(yubin_settings.MAILER_FILE_STORAGE_DIR, f"{str(uuid4())}.msg")

    @classmethod
    def admin_display_message_data(cls, model_admin, message):
        return f'''
            <div>
                <a href="{default_storage.url(message._message_data)}">
                    {message._message_data}
                </a>
            </div>
            <br>
            {super(cls, cls).admin_display_message_data(model_admin, message)}
        '''.strip()
