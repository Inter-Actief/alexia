# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def convert_availability_nature(apps, schema_editor):
    """
    Convert existing Yes-availabilities to Assigned.
    """
    Availability = apps.get_model("scheduling", "Availability")
    Availability.objects.filter(nature='Y').update(nature='A')


def reverse_convert_availability_nature(apps, schema_editor):
    """
    Convert existing Assigned-availabilities to Yes.
    """
    Availability = apps.get_model("scheduling", "Availability")
    Availability.objects.filter(nature='A').update(nature='N')


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0005_assign_tenders_availability'),
    ]

    operations = [
        migrations.RunPython(convert_availability_nature, reverse_convert_availability_nature),
    ]
