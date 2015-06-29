# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_auto_20150203_0239'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sellingprice',
            unique_together=set([('pricegroup', 'productgroup')]),
        ),
    ]
