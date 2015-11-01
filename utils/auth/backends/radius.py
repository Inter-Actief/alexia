from django.conf import settings
from django.contrib.auth.models import User

from apps.organization.models import Profile

import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary


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
        except Exception, e:
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
            try:
                profile = Profile.objects.get(radius_username=username)
                return profile.user
            except Profile.DoesNotExist:
                # may be create the user?
                user = User(username=username)
                user.set_unusable_password()
                user.save()
                profile = Profile(user=user, radius_username=username)
                profile.save()
                return user

    def get_user(self, user_id):
        """Retrieves an user by its id."""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
