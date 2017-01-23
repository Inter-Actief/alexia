import pyrad.packet
from django.conf import settings
from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend
from pyrad.client import Client
from pyrad.dictionary import Dictionary

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
    def authenticate(self, username=None, password=None):
        srv = Client(server=settings.RADIUS_HOST, authport=settings.RADIUS_PORT,
                     secret=settings.RADIUS_SECRET.encode(), dict=Dictionary(settings.RADIUS_DICT))

        req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username.encode())
        req["User-Password"] = req.PwCrypt(password)

        reply = srv.SendPacket(req)

        if reply.code == pyrad.packet.AccessAccept:
            backend = self.__module__ + "." + self.__class__.__name__
            user, created = get_or_create_user(backend, username)
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
