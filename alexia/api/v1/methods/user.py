from typing import Dict

from django.contrib.auth.models import User
from django.db import transaction
from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import manager_required, login_required
from alexia.api.exceptions import InvalidParamsError, ObjectNotFoundError
from alexia.apps.organization.models import (
    AuthenticationData, Certificate, Membership, Profile,
)
from alexia.auth.backends import OIDC_BACKEND_NAME

from ..common import format_certificate, format_user


@rpc_method(name='user.add', entry_point='v1')
@manager_required
@transaction.atomic
def user_add(radius_username: str, first_name: str, last_name: str, email: str, **kwargs) -> Dict:
    """
    **Signature**: `user.add(radius_username, first_name, last_name, email)`

    **Arguments**:

    - `radius_username` : `str` -- Unique username
    - `first_name` : `str` -- First name
    - `last_name` : `str` -- Last name
    - `email` : `str` -- Valid email address

    **Return type**: `dict`

    **Idempotent**: no

    **Required user level**: Manager

    **Documentation**:

    Add a new user to Alexia.

    A user must have a unique username and a valid email address.

    Returns the user information on success.

    **Example return value**:

        {
          "first_name": "John",
          "last_name": "Doe",
          "radius_username": "s0000000"
        }

    **Raises errors**:

    - `-32602` (Invalid params) if the username already exists.
    """
    if User.objects.filter(username=radius_username).exists() or \
            AuthenticationData.objects.filter(backend=OIDC_BACKEND_NAME, username__iexact=radius_username).exists():
        raise InvalidParamsError('User with provided username already exists')

    user = User(username=radius_username, first_name=first_name, last_name=last_name, email=email)
    user.save()

    data = AuthenticationData(user=user, backend=OIDC_BACKEND_NAME, username=radius_username.lower())
    data.save()

    user.profile = Profile()
    user.profile.save()

    return format_user(user)


@rpc_method(name='user.exists', entry_point='v1')
@login_required
def user_exists(radius_username: str, **kwargs) -> bool:
    """
    **Signature**: `user.exists(radius_username)`

    **Arguments**:

    - `radius_username` : `str` -- Username to search for

    **Return type**: `bool`

    **Idempotent**: yes

    **Required user level**: User

    **Documentation**:

    Check if a user exists by his or her username.

    Returns `True` when the username exists, `False` otherwise.
    """
    return User.objects.filter(authenticationdata__backend=OIDC_BACKEND_NAME,
                               authenticationdata__username=radius_username).exists()


@rpc_method(name='user.get', entry_point='v1')
@login_required
def user_get(radius_username: str, **kwargs) -> Dict:
    """
    **Signature**: `user.get(radius_username)`

    **Arguments**:

    - `radius_username` : `str` -- Username to search for.

    **Return type**: `dict`

    **Idempotent**: yes

    **Required user level**: User

    **Documentation**:

    Retrieve information about a specific user.

    Returns an object representing the user. Result contains `first_name`, `last_name` and `radius_username`.

    **Example return value**:

        {
          "first_name": "John",
          "last_name": "Doe",
          "radius_username": "s0000000"
        }

    **Raises errors**:

    - `404` (Object not found) if the provided username cannot be found.
    """
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise ObjectNotFoundError

    return format_user(user)


@rpc_method(name='user.get_by_id', entry_point='v1')
@login_required
def user_get_by_id(user_id: int, **kwargs) -> Dict:
    """
    **Signature**: `user.get_by_id(radius_username)`

    **Arguments**:

    - `user_id` : `int` -- User id to search for.

    **Return type**: `dict`

    **Idempotent**: yes

    **Required user level**: User

    **Documentation**:

    Retrieve information about a specific user.

    **Example return value**:

        {
          "first_name": "John",
          "last_name": "Doe",
          "radius_username": "s0000000"
        }

    **Raises errors**:

    - `404` (Object not found) if the provided username cannot be found.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ObjectNotFoundError

    return format_user(user)


@rpc_method(name='user.get_membership', entry_point='v1')
@manager_required
def user_get_membership(radius_username: str, **kwargs) -> Dict:
    """
    **Signature**: `user.get_membership(radius_username)`

    **Arguments**:

    - `radius_username` : `str` -- Username to search for.

    **Return type**: `dict`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Retrieve the membership details for a specific user for the current organization.

    **Example return value**:

        {
          "user": "s0000000",
          "organization": "Inter-Actief",
          "comments": "",
          "is_tender": True,
          "is_planner": False,
          "is_manager": False,
          "is_active": True
        }

    **Raises errors**:

    - `404` (Object not found) if the provided username cannot be found or the user has no membership with the current organization.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
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


@rpc_method(name='user.get_iva_certificate', entry_point='v1')
@manager_required
def user_get_iva_certificate(radius_username: str, **kwargs) -> Dict:
    """
    **Signature**: `user.get_iva_certificate(radius_username)`

    **Arguments**:

    - `radius_username` : `str` -- Username to search for.

    **Return type**: `dict`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Retrieve the IVA certificate file for a specific user.

    **Example return value**:

        {
          "user": "s0000000",
          "certificate_data": "U29tZSBiYXNlIDY0IHRleHQgdGhhdCBtaWdodCBiZ.........BhIGxvdCBsb25nZXIgdGhhbiB0aGlzIGlzLi4u"
        }

    **Raises errors**:

    - `404` (Object not found) if provided username cannot be found or the user has no IVA certificate.

    """
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise ObjectNotFoundError

    try:
        certificate = Certificate.objects.get(owner=user)
    except Certificate.DoesNotExist:
        raise ObjectNotFoundError

    return format_certificate(certificate)
