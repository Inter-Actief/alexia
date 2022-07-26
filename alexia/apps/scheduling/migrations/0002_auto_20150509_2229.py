# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='ends_at',
            field=models.DateTimeField(verbose_name='ends at', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='starts_at',
            field=models.DateTimeField(verbose_name='starts at', db_index=True),
            preserve_default=True,
        ),
    ]
