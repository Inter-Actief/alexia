# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0001_initial'),
        ('scheduling', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryproduct',
            name='event',
            field=models.ForeignKey(related_name='temporaryproducts', verbose_name='event', to='scheduling.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sellingprice',
            name='pricegroup',
            field=models.ForeignKey(verbose_name='price group', to='billing.PriceGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sellingprice',
            name='productgroup',
            field=models.ForeignKey(verbose_name='product group', to='billing.ProductGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rfidcard',
            name='managed_by',
            field=models.ManyToManyField(to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rfidcard',
            name='user',
            field=models.ForeignKey(related_name='rfids', verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='purchase',
            name='order',
            field=models.ForeignKey(related_name='purchases', verbose_name='order', to='billing.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='purchase',
            name='product',
            field=models.ForeignKey(related_name='purchases', verbose_name='product', to='billing.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productgroup',
            name='organization',
            field=models.ForeignKey(related_name='productgroups', verbose_name='organization', to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pricegroup',
            name='organization',
            field=models.ForeignKey(related_name='pricegroups', verbose_name='organization', to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pricegroup',
            name='productgroups',
            field=models.ManyToManyField(related_name='pricegroups', verbose_name='product groups', through='billing.SellingPrice', to='billing.ProductGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permanentproduct',
            name='organization',
            field=models.ForeignKey(related_name='products', verbose_name='organization', to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permanentproduct',
            name='productgroup',
            field=models.ForeignKey(verbose_name='product group', to='billing.ProductGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='added_by',
            field=models.ForeignKey(related_name='+', verbose_name='added by', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='authorization',
            field=models.ForeignKey(related_name='orders', verbose_name='authorization', to='billing.Authorization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='event',
            field=models.ForeignKey(related_name='orders', verbose_name='event', to='scheduling.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authorization',
            name='organization',
            field=models.ForeignKey(related_name='authorizations', verbose_name='organization', to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='authorization',
            name='user',
            field=models.ForeignKey(related_name='authorizations', verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
