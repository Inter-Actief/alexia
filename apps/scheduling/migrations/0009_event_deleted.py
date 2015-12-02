# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0008_enrollclosed_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='deleted',
            field=models.BooleanField(default=False, verbose_name='deleted'),
        ),
    ]
