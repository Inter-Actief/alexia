from django.contrib.auth.models import User
from django.db import transaction
from jsonrpc import jsonrpc_method

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError, ObjectNotFoundError
from alexia.apps.organization.models import (
    AuthenticationData, Certificate, Membership, Profile,
)
from alexia.auth.backends import RADIUS_BACKEND_NAME, SAML2_BACKEND_NAME

from ..common import format_certificate, format_user
from ..config import api_v1_site


@jsonrpc_method('user.add(radius_username=String, first_name=String, last_name=String, email=String) -> Object',
                site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic
def user_add(request, radius_username, first_name, last_name, email):
    """
    Add a new user to Alexia.

    An user must have an unique username and a valid email address.

    Returns the user information on success.

    radius_username  -- Unique username
    first_name       -- First name
    last_name        -- Last name
    email            -- Valid email address

    Example result value:
    {
        "first_name": "John",
        "last_name": "Doe",
        "radius_username": "s0000000"
    }

    Raises error -32602 (Invalid params) if the username already exists.
    """
    if User.objects.filter(username=radius_username).exists() or \
            AuthenticationData.objects.filter(backend=RADIUS_BACKEND_NAME, username__iexact=radius_username).exists() \
            or AuthenticationData.objects.filter(backend=SAML2_BACKEND_NAME, username__iexact=radius_username).exists():
        raise InvalidParamsError('User with provided username already exists')

    user = User(username=radius_username, first_name=first_name, last_name=last_name, email=email)
    user.save()

    data = AuthenticationData(user=user, backend=SAML2_BACKEND_NAME, username=radius_username.lower())
    data.save()

    user.profile = Profile()
    user.profile.save()

    return format_user(user)


@jsonrpc_method('user.exists(radius_username=String) -> Boolean', site=api_v1_site, authenticated=True, safe=True)
def user_exists(request, radius_username):
    """
    Check if a user exists by his or her username.

    Returns true when the username exists, false otherwise.

    radius_username    -- Username to search for.
    """
    return User.objects.filter(authenticationdata__backend=RADIUS_BACKEND_NAME,
                               authenticationdata__username=radius_username).exists() or \
           User.objects.filter(authenticationdata__backend=SAML2_BACKEND_NAME,
                               authenticationdata__username=radius_username).exists() or \
            User.objects.filter(username=radius_username).exists()


@jsonrpc_method('user.get(radius_username=String) -> Object', site=api_v1_site, authenticated=True, safe=True)
def user_get(request, radius_username):
    """
    Retrieve information about a specific user.

    Returns a object representing the user. Result contains first_name,
    last_name and radius_username.

    radius_username    -- Username to search for.

    Raises error 404 if provided username cannot be found.

    Example result value:
    {
        "first_name": "John",
        "last_name": "Doe",
        "radius_username": "s0000000"
    }
    """
    try:
        user = User.objects.get(authenticationdata__backend=SAML2_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except:
            raise ObjectNotFoundError

    return format_user(user)


@jsonrpc_method('user.get_by_id(user_id=Number) -> Object', site=api_v1_site, authenticated=True, safe=True)
def user_get_by_id(request, user_id):
    """
    Retrieve information about a specific user.

    user_id    -- User id to search for.

    Raises error 404 if provided username cannot be found.

    Example result value:
    {
        "first_name": "John",
        "last_name": "Doe",
        "radius_username": "s0000000"
    }
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ObjectNotFoundError

    return format_user(user)


@jsonrpc_method(
    'user.get_membership(radius_username=String) -> Object',
    site=api_v1_site,
    safe=True,
    authenticated=True
)
@manager_required
def user_get_membership(request, radius_username):
    """
    Retrieve the membership details for a specific user for the current organization.

    Required user level: Manager

    radius_username     -- Username to search for.

    Raises error 404 if the provided username cannot be found or the user has no membership with the current
    organization.

    Example result value:
    {
        "user": "s0000000",
        "organization": "Inter-Actief",
        "comments": "",
        "is_tender": True,
        "is_planner": False,
        "is_manager": False,
        "is_active": True
    }
    """
    try:
        user = User.objects.get(authenticationdata__backend=SAML2_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except:
            raise ObjectNotFoundError

    try:
        membership = Membership.objects.get(
            user=user,
            organization=request.organization
        )
    except Membership.DoesNotExist:
        raise ObjectNotFoundError

    return {
        "user": user.username,
        "organization": request.organization.name,
        "comments": membership.comments,
        "is_tender": membership.is_tender,
        "is_planner": membership.is_planner,
        "is_manager": membership.is_manager,
        "is_active": membership.is_active
    }


@jsonrpc_method(
    'user.get_iva_certificate(radius_username=String) -> Object',
    site=api_v1_site,
    safe=True,
    authenticated=True
)
@manager_required
def user_get_iva_certificate(request, radius_username):
    """
    Retrieve the IVA certificate file for a specific user.

    Required user level: Manager

    radius_username    -- Username to search for.

    Raises error 404 if provided username cannot be found or the user has no IVA certificate.

    Example result value:
    {
        "user": "s0000000",
        "certificate_data": "U29tZSBiYXNlIDY0IHRleHQgdGhhdCBtaWdodCBiZ.........BhIGxvdCBsb25nZXIgdGhhbiB0aGlzIGlzLi4u"
    }
    """
    try:
        user = User.objects.get(authenticationdata__backend=SAML2_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except:
            raise ObjectNotFoundError

    try:
        certificate = Certificate.objects.get(owner=user)
    except Certificate.DoesNotExist:
        raise ObjectNotFoundError

    return format_certificate(certificate)
