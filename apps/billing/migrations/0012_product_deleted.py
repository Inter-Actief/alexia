# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_alter_order_purchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='deleted',
            field=models.BooleanField(default=False, verbose_name='deleted'),
        ),
    ]
