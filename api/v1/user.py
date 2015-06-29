from django.db import transaction
from jsonrpc import jsonrpc_method
from django.contrib.auth.models import User

from .common import api_v1_site, format_user
from .exceptions import NotFoundError, InvalidParametersError
from apps.organization.models import Profile
from utils.auth.decorators import manager_required


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
            Profile.objects.filter(radius_username=radius_username).exists():
        raise InvalidParametersError('User with provided radius_username already exists')

    user = User(username=radius_username, first_name=first_name, last_name=last_name, email=email)
    user.save()

    user.profile = Profile(radius_username=radius_username)
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

    return User.objects.filter(profile__radius_username=radius_username).exists()


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
        user = User.objects.get(profile__radius_username=radius_username)
    except User.DoesNotExist:
        raise NotFoundError

    return format_user(user)
