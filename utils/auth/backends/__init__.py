from django.contrib.auth.models import User

from apps.organization.models import Profile, AuthenticationData

RADIUS_BACKEND_NAME = "utils.auth.backends.radius.RadiusBackend"


def get_or_create_user(backend, username):
    try:
        authentication_data = AuthenticationData.objects.get(backend=backend, username=username)
        return authentication_data.user, False
    except AuthenticationData.DoesNotExist:
        user = User(username=username)
        user.set_unusable_password()
        user.save()

        data = AuthenticationData(user=user, backend=backend, username=username.lower())
        data.save()

        profile = Profile(user=user)
        profile.save()

        return user, True
