# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0008_order_rfidcard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='rfidcard',
            field=models.ForeignKey(verbose_name='rfid card', blank=True, to='billing.RfidCard', null=True, on_delete=models.SET_NULL),
        ),
    ]
