# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_alter_order_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfidcard',
            name='atqa',
            field=models.CharField(default="", max_length=16, verbose_name='atqa'),
        ),
        migrations.AddField(
            model_name='rfidcard',
            name='sak',
            field=models.CharField(default="", max_length=16, verbose_name='sak'),
        ),
        migrations.RenameField(
            model_name='rfidcard',
            old_name='identifier',
            new_name='uid'
        ),
        migrations.AlterField(
            model_name='rfidcard',
            name='uid',
            field=models.CharField(default="", max_length=32, verbose_name='uid'),
            preserve_default=False,
        ),
    ]
