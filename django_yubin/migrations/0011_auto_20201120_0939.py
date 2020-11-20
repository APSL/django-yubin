# Generated by Django 3.1.3 on 2020-11-20 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_yubin', '0010_auto_20201118_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Created'), (1, 'Queued'), (2, 'In process'), (3, 'Sent'), (4, 'Failed'), (5, 'Blacklisted'), (6, 'Discarded')], default=0, verbose_name='action'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Created'), (1, 'Queued'), (2, 'In process'), (3, 'Sent'), (4, 'Failed'), (5, 'Blacklisted'), (6, 'Discarded')], default=0),
        ),
    ]