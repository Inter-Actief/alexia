from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
from django_auth_ldap.backend import LDAPBackend

from django.conf import settings
from django.contrib.auth import get_user_model

from alexia.apps.organization.models import AuthenticationData, Profile

User = get_user_model()
RADIUS_BACKEND_NAME = 'utils.auth.backends.radius.RadiusBackend'


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


class MultiLDAPBackend(LDAPBackend):
    def get_or_create_user(self, username, ldap_user):
        backend = self.__module__ + "." + self.__class__.__name__
        return get_or_create_user(backend, username)


class RadiusBackend(object):
    """Authenticator against a RADIUS server."""

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        """Authenticate against the RADIUS server"""

        # Create a RADIUS client
        radius_dict = Dictionary(settings.RADIUS_DICT)
        client = Client(server=settings.RADIUS_HOST,
                        authport=settings.RADIUS_PORT,
                        secret=settings.RADIUS_SECRET.encode('utf-8'),  # avoid UnicodeDecodeError
                        dict=radius_dict,
                        )

        # Create a packet ...
        req = client.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                                      User_Name=username.encode('utf-8'),
                                      )
        req["User-Password"] = req.PwCrypt(password)

        # .. and send it
        try:
            reply = client.SendPacket(req)
        except Exception:
            # Something went wrong with the packet. Just fall through
            return None

        # Handle the reply
        if reply.code == pyrad.packet.AccessReject:
            # Access was rejected
            return None
        elif reply.code != pyrad.packet.AccessAccept:
            # Some error
            return None
        else:
            backend = self.__module__ + "." + self.__class__.__name__
            user, created = get_or_create_user(backend, username)
            return user

    def get_user(self, user_id):
        """Retrieves an user by its id."""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
