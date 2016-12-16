from django.contrib.auth.models import User
from django.db import transaction
from jsonrpc import jsonrpc_method

from alexia.apps.organization.models import AuthenticationData, Profile
from alexia.auth.backends import RADIUS_BACKEND_NAME
from alexia.auth.decorators import manager_required

from .common import api_v1_site, format_user
from .exceptions import InvalidParametersError, NotFoundError


@jsonrpc_method('user.add(radius_username=String, first_name=String, last_name=String, email=String) -> Object',
                site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def user_add(request, radius_username, first_name, last_name, email):
    """
    Add a new user to Alexia.

    An user must have an unique radius_username and a valid email address.

    Returns the user information on success.

    radius_username  -- Unique RADIUS username
    first_name       -- First name
    last_name        -- Last name
    email            -- Valid email address

    Example result value:
    {
        "first_name": "John",
        "last_name": "Doe",
        "radius_username": "s0000000"
    }

    Raises error -32602 (Invalid params) if the radius_username already exists.
    """
    if User.objects.filter(username=radius_username).exists() or \
            AuthenticationData.objects.filter(backend=RADIUS_BACKEND_NAME, username__iexact=radius_username).exists():
        raise InvalidParametersError('User with provided radius_username already exists')

    user = User(username=radius_username, first_name=first_name, last_name=last_name, email=email)
    user.save()

    data = AuthenticationData(user=user, backend=RADIUS_BACKEND_NAME, username=radius_username.lower())
    data.save()

    user.profile = Profile()
    user.profile.save()

    return format_user(user)


@jsonrpc_method('user.exists(radius_username=String) -> Boolean',
                site=api_v1_site, authenticated=True, safe=True)
def user_exists(request, radius_username):
    """
    Check if a user exists by his or her RADIUS username.

    Returns true when the username exists, false otherwise.

    radius_username    -- RADIUS username to search for.
    """

    return User.objects.filter(authenticationdata__backend=RADIUS_BACKEND_NAME,
                               authenticationdata__username=radius_username).exists()


@jsonrpc_method('user.get(radius_username=String) -> Object',
                site=api_v1_site, authenticated=True, safe=True)
def user_get(request, radius_username):
    """
    Retrieve information about a specific user.

    Returns a object representing the user. Result contains first_name,
    last_name and radius_username.

    radius_username    -- RADIUS username to search for.

    Raises error 404 if provided username cannot be found.

    Example result value:
    {
        "first_name": "John",
        "last_name": "Doe",
        "radius_username": "s0000000"
    }
    """

    try:
        user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise NotFoundError

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
        raise NotFoundError

    return format_user(user)
