# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Authorization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='start date')),
                ('end_date', models.DateTimeField(null=True, verbose_name='end date', blank=True)),
                ('account', models.CharField(max_length=32, verbose_name='account', blank=True)),
            ],
            options={
                'verbose_name': 'authorization',
                'verbose_name_plural': 'authorizations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('placed_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='placed at')),
                ('synchronized', models.BooleanField(default=False, verbose_name='synchronized')),
                ('amount', models.DecimalField(null=True, verbose_name='amount', max_digits=15, decimal_places=2)),
            ],
            options={
                'verbose_name': 'order',
                'verbose_name_plural': 'orders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PriceGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
            ],
            options={
                'verbose_name': 'price group',
                'verbose_name_plural': 'price groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PermanentProduct',
            fields=[
                ('product_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='billing.Product')),
            ],
            options={
            },
            bases=('billing.product',),
        ),
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
            ],
            options={
                'verbose_name': 'product group',
                'verbose_name_plural': 'product groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('price', models.DecimalField(verbose_name='price', max_digits=15, decimal_places=2)),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RfidCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=50, verbose_name='identifier')),
                ('is_active', models.BooleanField(default=False, verbose_name='is active')),
                ('registered_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='registered at')),
            ],
            options={
                'verbose_name': 'RFID card',
                'verbose_name_plural': 'RFID cards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SellingPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(verbose_name='price', max_digits=15, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryProduct',
            fields=[
                ('product_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='billing.Product')),
                ('price', models.DecimalField(verbose_name='price', max_digits=15, decimal_places=2)),
            ],
            options={
            },
            bases=('billing.product',),
        ),
    ]
