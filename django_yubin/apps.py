from django.apps import AppConfig


class YubinConfig(AppConfig):
    name = "django_yubin"
    # TODO: once < 3.2 support is dropped, this can be changed to BigAutoField
    default_auto_field = "django.db.models.AutoField"
