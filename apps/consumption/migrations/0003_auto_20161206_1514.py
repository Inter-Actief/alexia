# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-06 14:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consumption', '0002_auto_20161206_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(verbose_name='amount')),
            ],
            options={
                'verbose_name': 'unit entry',
                'verbose_name_plural': 'unit entries',
            },
        ),
        migrations.CreateModel(
            name='WeightEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_weight', models.DecimalField(decimal_places=1, max_digits=4, verbose_name='starting weight')),
                ('end_weight', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True, verbose_name='end weight')),
                ('kegs_changed', models.PositiveSmallIntegerField(default=0, verbose_name='kegs changed')),
                ('flow_start', models.DecimalField(decimal_places=1, max_digits=6, verbose_name='flowmeter start')),
                ('flow_end', models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True, verbose_name='flowmeter end')),
            ],
            options={
                'verbose_name': 'weight entry',
                'verbose_name_plural': 'weight entries',
            },
        ),
        migrations.AlterField(
            model_name='consumptionform',
            name='comments',
            field=models.TextField(blank=True, verbose_name='comments'),
        ),
        migrations.AddField(
            model_name='weightentry',
            name='consumption_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumption.ConsumptionForm', verbose_name='consumption_form'),
        ),
        migrations.AddField(
            model_name='weightentry',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consumption.WeightConsumptionProduct', verbose_name='product'),
        ),
        migrations.AddField(
            model_name='unitentry',
            name='consumption_form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='consumption.ConsumptionForm', verbose_name='consumption_form'),
        ),
        migrations.AddField(
            model_name='unitentry',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consumption.ConsumptionProduct', verbose_name='product'),
        ),
    ]