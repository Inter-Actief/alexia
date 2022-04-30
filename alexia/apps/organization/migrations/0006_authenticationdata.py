# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0005_organization_assigns_tenders'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthenticationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(max_length=50, verbose_name='Authentication backend')),
                ('username', models.CharField(max_length=50, verbose_name='Username')),
                ('additional_data', models.TextField(null=True, verbose_name='Additional data')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)),
            ],
        ),
    ]
