from django.apps import AppConfig


class YubinConfig(AppConfig):
    name = 'django_yubin'
    verbose_name = 'Django Yubin'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals  # noqa
