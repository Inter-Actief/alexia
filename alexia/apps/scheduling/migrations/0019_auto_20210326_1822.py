# Generated by Django 2.1.15 on 2021-03-26 17:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0018_auto_20170306_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='organization.Organization', verbose_name='organization'),
        ),
        migrations.AlterField(
            model_name='bartenderavailability',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduling.Availability', verbose_name='availability'),
        ),
        migrations.AlterField(
            model_name='bartenderavailability',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bartender_availabilities', to='scheduling.Event', verbose_name='event'),
        ),
        migrations.AlterField(
            model_name='bartenderavailability',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bartender_availability_set', to=settings.AUTH_USER_MODEL, verbose_name='bartender'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='organization.Organization', verbose_name='organizer'),
        ),
        migrations.AlterField(
            model_name='mailtemplate',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.Organization', verbose_name='organization'),
        ),
    ]
