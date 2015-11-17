# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_alter_order_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='added_by',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='added by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='authorization',
            field=models.ForeignKey(related_name='orders', on_delete=django.db.models.deletion.PROTECT, verbose_name='authorization', to='billing.Authorization'),
        ),
        migrations.AlterField(
            model_name='order',
            name='event',
            field=models.ForeignKey(related_name='orders', on_delete=django.db.models.deletion.PROTECT, verbose_name='event', to='scheduling.Event'),
        ),
        migrations.AlterField(
            model_name='order',
            name='rfidcard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='rfid card', blank=True, to='billing.RfidCard', null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='order',
            field=models.ForeignKey(related_name='purchases', on_delete=django.db.models.deletion.PROTECT, verbose_name='order', to='billing.Order'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(related_name='purchases', on_delete=django.db.models.deletion.PROTECT, verbose_name='product', to='billing.Product'),
        ),
    ]
