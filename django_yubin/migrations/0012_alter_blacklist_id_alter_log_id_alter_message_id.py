# Generated by Django 4.2.4 on 2024-06-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_yubin', '0011_message_bcc_address_message_cc_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='log',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='message',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
