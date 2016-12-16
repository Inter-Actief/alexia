# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0003_auto_20150903_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='bartenders',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='bartenders', through='scheduling.BartenderAvailability', blank=True),
        ),
    ]
