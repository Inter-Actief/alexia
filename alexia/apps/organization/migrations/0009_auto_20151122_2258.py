# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_remove_profile_radius_username'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='authenticationdata',
            unique_together=set([('user', 'backend'), ('backend', 'username')]),
        ),
    ]
