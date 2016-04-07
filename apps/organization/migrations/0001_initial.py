# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations

import apps.organization.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=apps.organization.models.get_certificate_path, verbose_name='certificate')),
                ('uploaded_at', models.DateField(auto_now_add=True, verbose_name='uploaded at')),
                ('approved_at', models.DateField(null=True, verbose_name='approved at')),
                ('approved_by', models.ForeignKey(related_name='approved_certificates', verbose_name='approved by', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('is_public', models.BooleanField(default=False, verbose_name='is public')),
                ('prevent_conflicting_events', models.BooleanField(default=True, verbose_name='prevent conflicting events')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'location',
                'verbose_name_plural': 'locations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('is_tender', models.BooleanField(default=False, verbose_name='may tend on events')),
                ('is_planner', models.BooleanField(default=False, verbose_name='may create and modify events')),
                ('is_manager', models.BooleanField(default=False, verbose_name='may create and modify users')),
            ],
            options={
                'ordering': ('user', 'organization'),
                'verbose_name': 'membership',
                'verbose_name_plural': 'memberships',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug', unique=True, editable=False)),
                ('is_public', models.BooleanField(default=False, verbose_name='is public')),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='users', through='organization.Membership')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'organization',
                'verbose_name_plural': 'organizations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('radius_username', models.CharField(max_length=10, verbose_name='RADIUS username', blank=True)),
                ('is_iva', models.BooleanField(default=False, verbose_name='has IVA-certificate')),
                ('is_bhv', models.BooleanField(default=False, verbose_name='has BHV-certificate')),
                ('ical_id', models.CharField(max_length=32, null=True, verbose_name='iCal identifier')),
                ('certificate', models.OneToOneField(null=True, verbose_name='certificate', to='organization.Certificate')),
                ('current_organization', models.ForeignKey(verbose_name='current organization', to='organization.Organization', null=True)),
                ('user', models.OneToOneField(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
                'verbose_name': 'profile',
                'verbose_name_plural': 'profiles',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='membership',
            name='organization',
            field=models.ForeignKey(verbose_name='organization', to='organization.Organization'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'organization')]),
        ),
    ]
