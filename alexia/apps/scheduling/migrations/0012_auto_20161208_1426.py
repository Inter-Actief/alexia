# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-08 13:26
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0011_auto_20161206_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='kegs',
            field=models.PositiveSmallIntegerField(verbose_name='number of kegs'),
        ),
    ]
