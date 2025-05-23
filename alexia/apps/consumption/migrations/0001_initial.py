# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-06 11:09
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumptionProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='name')),
            ],
            options={
                'verbose_name': 'consumption product',
                'verbose_name_plural': 'consumption products',
            },
        ),
        migrations.CreateModel(
            name='WeightConsumptionProduct',
            fields=[
                ('consumptionproduct_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='consumption.ConsumptionProduct')),
                ('full_weight', models.DecimalField(decimal_places=1, max_digits=4, verbose_name='full weight')),
                ('empty_weight', models.DecimalField(decimal_places=1, max_digits=4, verbose_name='empty weight')),
                ('has_flowmeter', models.BooleanField(default=False, verbose_name='has flowmeter')),
            ],
            options={
                'verbose_name': 'consumption product by weight',
                'verbose_name_plural': 'consumption products by weight',
            },
            bases=('consumption.consumptionproduct',),
        ),
    ]
