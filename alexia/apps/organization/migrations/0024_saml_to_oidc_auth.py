# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


SAML2_BACKEND_NAME = 'utils.auth.backends.saml2.SAML2Backend'
OIDC_BACKEND_NAME = 'utils.auth.backends.oidc.OIDCBackend'


def convert_saml_to_oidc_auths(apps, schema_editor):
    """
    Convert existing SAML AuthenticationData to OIDC.
    """
    AuthenticationData = apps.get_model("organization", "AuthenticationData")
    radius_auths = AuthenticationData.objects.filter(backend=SAML2_BACKEND_NAME)

    for auth in radius_auths:
        AuthenticationData.objects.get_or_create(backend=OIDC_BACKEND_NAME, username=auth.username, user=auth.user)


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0023_organization_is_active'),
    ]

    operations = [
        migrations.RunPython(convert_saml_to_oidc_auths),
    ]
