from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from jsonrpc import jsonrpc_method

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError, ObjectNotFoundError
from alexia.apps.billing.models import Authorization
from alexia.auth.backends import RADIUS_BACKEND_NAME, SAML2_BACKEND_NAME

from ..common import format_authorization
from ..config import api_v1_site


@jsonrpc_method('authorization.list(radius_username=String) -> Array', site=api_v1_site, authenticated=True, safe=True)
@manager_required
def authorization_list(request, radius_username=None):
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
    result = []
    authorizations = Authorization.objects.filter(organization=request.organization)

    if radius_username is not None:
        user = get_user_by_username(radius_username)

        authorizations = authorizations.filter(user=user)

    authorizations = authorizations.select_related('user')

    for authorization in authorizations:
        result.append(format_authorization(authorization))

    return result


@jsonrpc_method('authorization.get(radius_username=String) -> Array', site=api_v1_site, authenticated=True, safe=True)
@manager_required
def authorization_get(request, radius_username):
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
    result = []

    user = get_user_by_username(radius_username)

    authorizations = Authorization.objects.filter(user=user, organization=request.organization)

    for authorization in authorizations:
        result.append({
            'id': authorization.pk,
            'start_date': authorization.start_date.isoformat(),
            'end_date': authorization.end_date.isoformat() if authorization.end_date else None,
        })

    return result


@jsonrpc_method(
    'authorization.add(radius_username=String, account=String) -> Object',
    site=api_v1_site,
    authenticated=True
)
@manager_required
@transaction.atomic
def authorization_add(request, radius_username, account):
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
    user = get_user_by_username(radius_username)

    authorization = Authorization(user=user, organization=request.organization)
    authorization.save()

    return format_authorization(authorization)


@jsonrpc_method('authorization.end(radius_username=String, authorization_id=Number) -> Boolean', site=api_v1_site,
                authenticated=True)
@manager_required
@transaction.atomic
def authorization_end(request, radius_username, authorization_id):
    """
    End an authorization from the specified user.

    Required user level: Manager

    Returns true when successful. Returns false when the authorization was already ended.

    radius_username    -- Username to search for.
    identifier         -- RFID card hardware identifier (max. 16 chars)

    Raises error -32602 (Invalid params) if the username does not exist.
    Raises error -32602 (Invalid params) if provided authorization cannot be found.
    """
    user = get_user_by_username(radius_username)

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

def get_user_by_username(radius_username):
    try:
        user = User.objects.get(authenticationdata__backend=SAML2_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=radius_username)
            except User.DoesNotExist:
                raise InvalidParamsError('User with provided username does not exits')
    return user
