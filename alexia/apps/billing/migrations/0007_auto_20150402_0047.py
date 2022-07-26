# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_auto_20150401_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfidcard',
            name='identifier',
            field=models.CharField(unique=True, max_length=50, verbose_name='identifier'),
            preserve_default=True,
        ),
    ]
