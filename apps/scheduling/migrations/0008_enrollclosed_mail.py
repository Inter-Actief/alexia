# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0007_event_is_risky'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailtemplate',
            name='name',
            field=models.CharField(max_length=32, verbose_name='name', choices=[(b'enrollopen', 'Enrollment open'), (b'enrollclosed', 'Enrollment closed'), (b'reminder', 'Weekly reminder')]),
        ),
    ]
