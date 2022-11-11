# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-12 12:20
import django.db.models.deletion
from django.db import migrations, models

import alexia.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_alter_order_purchase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='background_color',
            field=models.CharField(blank=True, help_text='Background color for Juliana', max_length=6, validators=[alexia.core.validators.validate_color], verbose_name='Background color'),
        ),
        migrations.AlterField(
            model_name='product',
            name='text_color',
            field=models.CharField(blank=True, help_text='Text color for Juliana', max_length=6, validators=[alexia.core.validators.validate_color], verbose_name='Text color'),
        ),
        migrations.AlterField(
            model_name='temporaryproduct',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='temporaryproducts', to='scheduling.Event', verbose_name='event'),
        ),
    ]
