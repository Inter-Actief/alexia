# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_location_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='assigns_tenders',
            field=models.BooleanField(default=False, verbose_name='assigns tenders'),
        ),
    ]
