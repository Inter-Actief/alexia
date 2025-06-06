# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-23 22:07
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0016_auto_20170116_2251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-starts_at'], 'verbose_name': 'event', 'verbose_name_plural': 'events'},
        ),
        migrations.AlterModelOptions(
            name='mailtemplate',
            options={'ordering': ['organization'], 'verbose_name': 'mail template', 'verbose_name_plural': 'mail templates'},
        ),
        migrations.AlterField(
            model_name='event',
            name='pricegroup',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='billing.PriceGroup', verbose_name='pricegroup'),
        ),
    ]
