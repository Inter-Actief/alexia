# -*- coding: utf-8 -*-
from django.db import migrations


RADIUS_BACKEND_NAME = 'utils.auth.backends.radius.RadiusBackend'
SAML2_BACKEND_NAME = 'utils.auth.backends.saml2.SAML2Backend'


def convert_radius_to_saml_auths(apps, schema_editor):
    """
    Convert existing Yes-availabilities to Assigned.
    """
    AuthenticationData = apps.get_model("organization", "AuthenticationData")
    radius_auths = AuthenticationData.objects.filter(backend=RADIUS_BACKEND_NAME)

    for auth in radius_auths:
        AuthenticationData.objects.get_or_create(backend=SAML2_BACKEND_NAME, username=auth.username, user=auth.user)


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0020_profile_nickname'),
    ]

    operations = [
        migrations.RunPython(convert_radius_to_saml_auths),
    ]
