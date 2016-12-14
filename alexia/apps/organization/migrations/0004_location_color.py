# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_organization_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='color',
            field=models.CharField(blank=True, max_length=6, verbose_name='Color', validators=[django.core.validators.RegexValidator(regex=b'^[0-9a-zA-Z]{6}$', message='Enter a valid hexadecimal color')]),
            preserve_default=True,
        ),
    ]
