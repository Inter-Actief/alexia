# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 08:42
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0017_auto_20170123_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='nature',
            field=models.CharField(choices=[('A', 'Assigned'), ('Y', 'Yes'), ('M', 'Maybe'), ('N', 'No')], max_length=1, verbose_name='nature'),
        ),
        migrations.AlterField(
            model_name='mailtemplate',
            name='name',
            field=models.CharField(choices=[('enrollopen', 'Enrollment open'), ('enrollclosed', 'Enrollment closed'), ('reminder', 'Weekly reminder')], max_length=32, verbose_name='name'),
        ),
    ]
