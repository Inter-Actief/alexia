# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_auto_20150203_0018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='permanentproduct',
            options={'ordering': ['organization', 'productgroup', 'position']},
        ),
        migrations.AddField(
            model_name='permanentproduct',
            name='position',
            field=models.IntegerField(default=1, verbose_name='position'),
            preserve_default=False,
        ),
    ]
