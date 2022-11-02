from abc import ABC, abstractmethod


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
    @abstractmethod
    def set_encoded_message(message, value):
        message._encoded_message = value


class FileStorageBackend(BaseStorageBackend):
    pass
