# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockcount',
            name='products',
            field=models.ManyToManyField(related_name='stockcounts', verbose_name='products', to='stock.StockProduct', through='stock.StockProductAmount', blank=True),
        ),
    ]
