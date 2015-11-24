# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_convert_radius_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='radius_username',
        ),
    ]
