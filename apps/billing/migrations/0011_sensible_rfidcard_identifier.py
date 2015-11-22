# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def convert_rfidcards(apps, schema_editor):
    RfidCard = apps.get_model("billing", "RfidCard")
    for card in RfidCard.objects.all():
        if card.uid[0:3] == '02,':
            card.atqa = '0004'
            card.sak = '08'
        elif card.uid[0:3] == '03,':
            card.atqa = '0002'
            card.sak = '18'
        elif card.uid[0:3] == '04,':
            card.atqa = '0344'
            card.sak = '20'
        elif card.uid[0:3] == '05,':
            card.atqa = '0044'
            card.sak = '00'
        card.uid = card.uid[3:]
        card.save()


def reverse_convert_rfidcards(apps, schema_editor):
    RfidCard = apps.get_model("billing", "RfidCard")
    for card in RfidCard.objects.all():
        if card.atqa == '0004' and card.sak == '08':
            card.uid = '02,%s' % card.uid
        elif card.atqa == '0002' and card.sak == '18':
            card.uid = '03,%s' % card.uid
        elif card.atqa == '0344' and card.sak == '20':
            card.uid = '04,%s' % card.uid
        elif card.atqa == '0044' and card.sak == '00':
            card.uid = '05,%s' % card.uid
        else:
            raise ValueError("RFID card (%s, %s, %s) cannot be downgraded to old database format" % (card.atqa, card.sak, card.uid))
        card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_alter_order_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='rfidcard',
            name='atqa',
            field=models.CharField(default="", max_length=16, verbose_name='ATQA', blank=True),
        ),
        migrations.AddField(
            model_name='rfidcard',
            name='sak',
            field=models.CharField(default="", max_length=16, verbose_name='SAK', blank=True),
        ),
        migrations.RenameField(
            model_name='rfidcard',
            old_name='identifier',
            new_name='uid'
        ),
        migrations.AlterField(
            model_name='rfidcard',
            name='uid',
            field=models.CharField(default="", max_length=32, verbose_name='UID'),
            preserve_default=False,
        ),
        migrations.RunPython(convert_rfidcards, reverse_convert_rfidcards)
    ]
