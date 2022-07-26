# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0006_convert_availability_nature'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_risky',
            field=models.BooleanField(default=False, verbose_name=b'risky'),
        ),
    ]
