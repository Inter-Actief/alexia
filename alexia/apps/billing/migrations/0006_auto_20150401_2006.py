# -*- coding: utf-8 -*-
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20150326_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='background_color',
            field=models.CharField(blank=True, help_text='Background color for Juliana', max_length=6, verbose_name='Background color', validators=[django.core.validators.RegexValidator(regex=b'^[0-9a-zA-Z]{6}$', message='Enter a valid hexadecimal color')]),
            preserve_default=True,
        ),
    ]
