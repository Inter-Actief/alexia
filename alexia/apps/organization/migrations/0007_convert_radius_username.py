from django.db import migrations

from alexia.auth.backends import RADIUS_BACKEND_NAME


def convert_radius_username(apps, schema_editor):
    """
    Convert existing RADIUS usernames in profiles to AuthenticationData-entries.
    """
    Profile = apps.get_model("organization", "Profile")
    AuthenticationData = apps.get_model("organization", "AuthenticationData")
    for profile in Profile.objects.exclude(radius_username=""):
        a = AuthenticationData(backend=RADIUS_BACKEND_NAME, username=profile.radius_username, user=profile.user)
        a.save()


def reverse_convert_radius_username(apps, schema_editor):
    """
    Convert existing RADIUS AuthenticationData-entries to usernames in profiles.
    Convert existing Assigned-availabilities to Yes.
    """
    Profile = apps.get_model("organization", "Profile")
    AuthenticationData = apps.get_model("organization", "AuthenticationData")
    for auth_data in AuthenticationData.objects.filter(backend=RADIUS_BACKEND_NAME):
        auth_data.user.profile.radius_username = auth_data.username
        auth_data.user.profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0006_authenticationdata'),
    ]

    operations = [
        migrations.RunPython(convert_radius_username, reverse_convert_radius_username),
    ]
