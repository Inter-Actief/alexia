# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_auto_20150127_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='background_color',
            field=models.CharField(blank=True, help_text='Background color for Juliana', max_length=6, verbose_name='Background username', validators=[django.core.validators.RegexValidator(regex=b'^[0-9a-zA-Z]{6}$', message='Enter a valid hexadecimal color')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='text_color',
            field=models.CharField(blank=True, help_text='Text color for Juliana', max_length=6, verbose_name='Text color', validators=[django.core.validators.RegexValidator(regex=b'^[0-9a-zA-Z]{6}$', message='Enter a valid hexadecimal color')]),
            preserve_default=True,
        ),
    ]
