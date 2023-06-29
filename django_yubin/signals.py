from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.module_loading import import_string

from . import settings as yubin_settings


@receiver(post_delete, sender='django_yubin.Message', dispatch_uid='django_yubin_delete_storage')
def delete_message_storage_callback(sender, **kwargs):
    """
    Deleting storage objects in the post_delete signal assures that they will be deleted always:
    from a single object, from a queryset or from the admin.

    https://docs.djangoproject.com/en/3.2/topics/db/models/#overriding-predefined-model-methods
    """
    if yubin_settings.MAILER_STORAGE_DELETE:
        message = kwargs['instance']
        storage_backend = import_string(message.storage)
        storage_backend.delete_message_data(message)
