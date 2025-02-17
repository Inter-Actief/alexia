# Generated by Django 2.2.28 on 2024-10-11 10:06

import alexia.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0025_organization_writeoff_enabled'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0021_auto_20240926_1621'),
        ('billing', '0018_product_shortcut'),
    ]

    operations = [
        migrations.CreateModel(
            name='WriteoffCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='name')),
                ('description', models.CharField(max_length=80, verbose_name='short description')),
                ('color', models.CharField(blank=True, max_length=6, validators=[alexia.core.validators.validate_color], verbose_name='color')),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.Organization', verbose_name='organization')),
            ],
        ),
        migrations.CreateModel(
            name='WriteOffOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='placed at')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='amount')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='added by')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='writeoff_orders', to='scheduling.Event', verbose_name='event')),
                ('writeoff_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='billing.WriteoffCategory', verbose_name='writeoff category')),
            ],
            options={
                'verbose_name': 'writeoff order',
                'verbose_name_plural': 'writeoff orders',
                'ordering': ['-placed_at'],
            },
        ),
        migrations.CreateModel(
            name='WriteOffPurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=32, verbose_name='product')),
                ('amount', models.PositiveSmallIntegerField(verbose_name='amount')),
                ('price', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='price')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writeoff_purchases', to='billing.WriteOffOrder', verbose_name='order')),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
        ),
    ]
