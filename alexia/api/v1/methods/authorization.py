from typing import List, Dict, Optional

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError
from alexia.apps.billing.models import Authorization
from alexia.auth.backends import OIDC_BACKEND_NAME

from ..common import format_authorization


@rpc_method(name='authorization.list', entry_point='v1')
@manager_required
def authorization_list(radius_username: Optional[str] = None, **kwargs) -> List[Dict]:
    """
    Retrieve registered authorizations for the current selected organization.

    Required user level: Manager

    Provide radius_username to select only authorizations of the provided user.

    Returns an array of accounts of registered authorizations.

    radius_username    -- (optional) Username to search for.

    Example return value:
    [
        {
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00",
            "user": "s0000000"
        }
    ]

    Raises error -32602 (Invalid params) if the username does not exist.
    """
    request = kwargs.get(REQUEST_KEY)
    result = []
    authorizations = Authorization.objects.filter(organization=request.organization)

    if radius_username is not None:
        try:
            user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except User.DoesNotExist:
            raise InvalidParamsError('User with provided username does not exist')

        authorizations = authorizations.filter(user=user)

    authorizations = authorizations.select_related('user')

    for authorization in authorizations:
        result.append(format_authorization(authorization))

    return result


@rpc_method(name='authorization.get', entry_point='v1')
@manager_required
def authorization_get(radius_username: str, **kwargs) -> List[Dict]:
    """
    Retrieve registered authorizations for a specified user and current selected
    organization.

    Required user level: Manager

    Returns an array of accounts of registered authorizations.

    radius_username    -- Username to search for.

    Example return value:
    [
        {
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00"
        }
    ]

    Raises error -32602 (Invalid params) if the username does not exist.
    """
    request = kwargs.get(REQUEST_KEY)
    result = []

    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    authorizations = Authorization.objects.filter(user=user, organization=request.organization)

    for authorization in authorizations:
        result.append({
            'id': authorization.pk,
            'start_date': authorization.start_date.isoformat(),
            'end_date': authorization.end_date.isoformat() if authorization.end_date else None,
        })

    return result


@rpc_method(name='authorization.add', entry_point='v1')
@manager_required
@transaction.atomic
def authorization_add(radius_username: str, account: str, **kwargs) -> Dict:
    """
    Add a new authorization to the specified user.

    Required user level: Manager

    Returns the authorization on success.

    radius_username    -- Username to search for.

    Example return value:
    {
        "id": 1,
        "end_date": null,
        "start_date": "2014-09-21T14:16:06+00:00",
        "user": "s0000000"
    }

    Raises error -32602 (Invalid params) if the username does not exist.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    authorization = Authorization(user=user, organization=request.organization)
    authorization.save()

    return format_authorization(authorization)


@rpc_method(name='authorization.end', entry_point='v1')
@manager_required
@transaction.atomic
def authorization_end(radius_username: str, authorization_id: int, **kwargs) -> bool:
    """
    End an authorization from the specified user.

    Required user level: Manager

    Returns true when successful. Returns false when the authorization was already ended.

    radius_username    -- Username to search for.
    identifier         -- RFID card hardware identifier (max. 16 chars)

    Raises error -32602 (Invalid params) if the username does not exist.
    Raises error -32602 (Invalid params) if provided authorization cannot be found.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    try:
        authorization = Authorization.objects.select_for_update().get(user=user,
                                                                      organization=request.organization,
                                                                      pk=authorization_id)
    except Authorization.DoesNotExist:
        raise InvalidParamsError('Authorization with id not found')

    if not authorization.end_date:
        authorization.end_date = timezone.now()
        authorization.save()
        return True
    else:
        return False
