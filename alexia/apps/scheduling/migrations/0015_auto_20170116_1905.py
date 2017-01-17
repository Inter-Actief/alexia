# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-16 18:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0014_remove_mailtemplate_send_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='availability',
            options={'verbose_name': 'availability type', 'verbose_name_plural': 'availability types'},
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'event', 'verbose_name_plural': 'events'},
        ),
        migrations.AlterModelOptions(
            name='mailtemplate',
            options={'verbose_name': 'mail template', 'verbose_name_plural': 'mail templates'},
        ),
    ]