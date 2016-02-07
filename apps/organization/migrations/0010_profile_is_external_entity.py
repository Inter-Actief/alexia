# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0009_auto_20151122_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_external_entity',
            field=models.BooleanField(default=False, verbose_name='is external entity'),
        ),
    ]
