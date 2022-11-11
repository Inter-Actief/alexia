# -*- coding: utf-8 -*-
from django.db import migrations


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
