# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0002_auto_20150509_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailtemplate',
            name='name',
            field=models.CharField(max_length=32, verbose_name='name', choices=[(b'enrollopen', 'Enrollment open'), (b'reminder', 'Weekly reminder')]),
            preserve_default=True,
        ),
    ]
