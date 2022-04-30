from django.conf import settings
from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend
from djangosaml2.backends import Saml2Backend

from alexia.apps.organization.models import AuthenticationData, Profile

User = get_user_model()
LDAP_BACKEND_NAME = 'utils.auth.backends.ldap.MultiLDAPBackend'
RADIUS_BACKEND_NAME = 'utils.auth.backends.radius.RadiusBackend'
SAML2_BACKEND_NAME = 'utils.auth.backends.saml2.SAML2Backend'


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
        backend = LDAP_BACKEND_NAME
        return get_or_create_user(backend, username)


class RadiusBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            import pyrad.packet
            from pyrad.client import Client, Timeout
            from pyrad.dictionary import Dictionary
        except ImportError:
            return None

        srv = Client(server=settings.RADIUS_HOST, authport=settings.RADIUS_PORT,
                     secret=settings.RADIUS_SECRET.encode(), dict=Dictionary(settings.RADIUS_DICT))

        req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username.encode())
        req["User-Password"] = req.PwCrypt(password)

        try:
            reply = srv.SendPacket(req)
        except Timeout:
            return None

        if reply.code == pyrad.packet.AccessAccept:
            backend = RADIUS_BACKEND_NAME
            user, created = get_or_create_user(backend, username)
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class AlexiaSAML2Backend(Saml2Backend):
    def configure_user(self, user, attributes, attribute_mapping):
        self._update_authentication_data(user)
        return super(AlexiaSAML2Backend, self).configure_user(user, attributes, attribute_mapping)
    
    def update_user(self, user, attributes, attribute_mapping,
                    force_save=False):
        self._update_authentication_data(user)
        return super(AlexiaSAML2Backend, self).update_user(user, attributes, attribute_mapping, force_save)

    def _update_authentication_data(self, user):
        try:
            authentication_data = AuthenticationData.objects.get(backend=SAML2_BACKEND_NAME, username=user.username)
            return authentication_data.user, False
        except AuthenticationData.DoesNotExist:
            data = AuthenticationData(user=user, backend=SAML2_BACKEND_NAME, username=user.username.lower())
            data.save()

        # Check if a profile exists
        Profile.objects.get_or_create(user=user)
