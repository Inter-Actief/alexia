# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='radius_username',
            field=models.CharField(unique=True, max_length=10, verbose_name='RADIUS username'),
            preserve_default=True,
        ),
    ]
