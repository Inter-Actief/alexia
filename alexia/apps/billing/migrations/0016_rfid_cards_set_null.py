# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 21:45
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0015_auto_20170116_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='rfidcard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='billing.RfidCard', verbose_name='rfid card'),
        ),
    ]
