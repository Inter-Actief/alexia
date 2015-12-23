# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0012_product_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permanentproduct',
            name='productgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='product group', to='billing.ProductGroup', null=True),
        ),
    ]
