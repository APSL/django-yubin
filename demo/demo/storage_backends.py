from django.core.files.storage import FileSystemStorage

from django_yubin.storage_backends import FileStorageBackend


class _InmutableFileSystemStorage(FileSystemStorage):
    def delete(self, name):
        pass


class InmutableFileStorageBackend(FileStorageBackend):
    storage = _InmutableFileSystemStorage()
