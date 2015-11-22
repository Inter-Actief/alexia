# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0011_sensible_rfidcard_identifier'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rfidcard',
            unique_together=set([('atqa', 'sak', 'uid')]),
        ),
    ]
