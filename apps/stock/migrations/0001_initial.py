# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('used_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='used at')),
                ('tap', models.PositiveSmallIntegerField(null=True, verbose_name='tap', blank=True)),
                ('start_weight', models.DecimalField(null=True, verbose_name='start weight', max_digits=5, decimal_places=2, blank=True)),
                ('end_weight', models.DecimalField(null=True, verbose_name='end weight', max_digits=5, decimal_places=2, blank=True)),
            ],
            options={
                'verbose_name': 'consumption',
                'verbose_name_plural': 'consumptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventConsumption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('opened_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='opened at')),
                ('closed_at', models.DateTimeField(null=True, verbose_name='closed at', blank=True)),
                ('event', models.ForeignKey(verbose_name='event', to='scheduling.Event')),
            ],
            options={
                'ordering': ['opened_at'],
                'verbose_name': 'event consumption',
                'verbose_name_plural': 'event consumptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date')),
                ('is_completed', models.BooleanField(default=False, verbose_name='is completed')),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('organization', models.ForeignKey(related_name='stockcounts', verbose_name='organization', to='organization.Organization')),
            ],
            options={
                'get_latest_by': 'date',
                'verbose_name': 'stock count',
                'verbose_name_plural': 'stock counts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('ideal_amount', models.IntegerField(verbose_name='ideal amount')),
            ],
            options={
                'verbose_name': 'stock product',
                'verbose_name_plural': 'stock products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockProductAmount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField(verbose_name='amount')),
                ('product', models.ForeignKey(verbose_name='product', to='stock.StockProduct')),
                ('stockcount', models.ForeignKey(verbose_name='stock count', to='stock.StockCount')),
            ],
            options={
                'verbose_name': 'stock product amount',
                'verbose_name_plural': 'stock product amounts',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stockcount',
            name='products',
            field=models.ManyToManyField(related_name='stockcounts', to='stock.StockProduct', through='stock.StockProductAmount', blank=True, null=True, verbose_name='products'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stockcount',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consumption',
            name='group',
            field=models.ForeignKey(related_name='consumptions', verbose_name='consumption group', to='stock.EventConsumption'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consumption',
            name='product',
            field=models.ForeignKey(related_name='consumptions', verbose_name='product', to='stock.StockProduct'),
            preserve_default=True,
        ),
    ]
