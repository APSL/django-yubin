# Generated by Django 3.2.16 on 2022-11-30 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_yubin', '0009_auto_20221122_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='storage',
            field=models.CharField(default='django_yubin.storage_backends.DatabaseStorageBackend', max_length=200, verbose_name='storage backend'),
        ),
    ]