# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0007_auto_20150402_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='rfidcard',
            field=models.ForeignKey(verbose_name='rfid card', to='billing.RfidCard', null=True),
            preserve_default=True,
        ),
    ]
