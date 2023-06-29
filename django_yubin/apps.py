from django.apps import AppConfig


class YubinConfig(AppConfig):
    name = 'django_yubin'
    verbose_name = "Django Yubin"

    def ready(self):
        from . import signals  # noqa
