# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0009_alter_order_rfidcard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='amount',
            field=models.DecimalField(default=0, verbose_name='amount', max_digits=15, decimal_places=2),
            preserve_default=False,
        ),
    ]
