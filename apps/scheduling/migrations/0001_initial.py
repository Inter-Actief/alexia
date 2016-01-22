# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('nature', models.CharField(max_length=1, verbose_name='nature', choices=[(b'Y', 'Yes'), (b'M', 'Maybe'), (b'N', 'No')])),
                ('organization', models.ForeignKey(related_name='availabilities', verbose_name='organization', to='organization.Organization')),
            ],
            options={
                'ordering': ('organization', 'name'),
                'verbose_name': 'availability type',
                'verbose_name_plural': 'availability types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BartenderAvailability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('availability', models.ForeignKey(verbose_name='availability', to='scheduling.Availability')),
            ],
            options={
                'verbose_name': 'bartender availability',
                'verbose_name_plural': 'bartender availabilities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('starts_at', models.DateTimeField(verbose_name='starts at')),
                ('ends_at', models.DateTimeField(verbose_name='ends at')),
                ('is_closed', models.BooleanField(default=False, verbose_name='tender enrollment closed')),
                ('kegs', models.IntegerField(verbose_name='number of kegs')),
                ('option', models.BooleanField(default=False, verbose_name='option')),
                ('tender_comments', models.TextField(verbose_name='Tender comments', blank=True)),
                ('bartenders', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, verbose_name='bartenders', through='scheduling.BartenderAvailability', blank=True)),
                ('location', models.ManyToManyField(related_name='events', verbose_name='location', to='organization.Location')),
                ('organizer', models.ForeignKey(related_name='events', verbose_name='organizer', to='organization.Organization')),
                ('participants', models.ManyToManyField(related_name='participates', verbose_name='participants', to='organization.Organization')),
                ('pricegroup', models.ForeignKey(related_name='events', verbose_name='pricegroup', to='billing.PriceGroup')),
            ],
            options={
                'ordering': ('-starts_at',),
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('template', models.TextField(verbose_name='template')),
                ('is_active', models.BooleanField(default=False, verbose_name='is active')),
                ('send_at', models.PositiveIntegerField(null=True, verbose_name='send at', blank=True)),
                ('organization', models.ForeignKey(verbose_name='organization', to='organization.Organization')),
            ],
            options={
                'ordering': ('organization', 'name'),
                'verbose_name': 'mail template',
                'verbose_name_plural': 'mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardReservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_day', models.SmallIntegerField(verbose_name='start day', choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('start_time', models.TimeField(default=datetime.time(16, 0), verbose_name='start time')),
                ('end_day', models.PositiveSmallIntegerField(verbose_name='end day', choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('end_time', models.TimeField(default=datetime.time(23, 59, 59), verbose_name='end time')),
                ('location', models.ForeignKey(verbose_name='location', to='organization.Location')),
                ('organization', models.ForeignKey(verbose_name='organization', to='organization.Organization')),
            ],
            options={
                'verbose_name': 'standard reservation',
                'verbose_name_plural': 'standard reservations',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mailtemplate',
            unique_together=set([('organization', 'name')]),
        ),
        migrations.AddField(
            model_name='bartenderavailability',
            name='event',
            field=models.ForeignKey(related_name='bartender_availabilities', verbose_name='event', to='scheduling.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bartenderavailability',
            name='user',
            field=models.ForeignKey(related_name='bartender_availability_set', verbose_name='bartender', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bartenderavailability',
            unique_together=set([('user', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together=set([('organization', 'name')]),
        ),
    ]
