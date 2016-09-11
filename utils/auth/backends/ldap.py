from django_auth_ldap.backend import LDAPBackend

from utils.auth.backends import get_or_create_user


class MultiLDAPBackend(LDAPBackend):
    def get_or_create_user(self, username, ldap_user):
        backend = self.__module__ + "." + self.__class__.__name__
        return get_or_create_user(backend, username)
