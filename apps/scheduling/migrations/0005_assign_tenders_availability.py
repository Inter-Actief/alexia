# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0004_django18'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='nature',
            field=models.CharField(max_length=1, verbose_name='nature', choices=[(b'A', 'Assigned'), (b'Y', 'Yes'), (b'M', 'Maybe'), (b'N', 'No')]),
        ),
    ]
