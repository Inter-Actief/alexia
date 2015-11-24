from django.db import transaction
from jsonrpc import jsonrpc_method
from django.contrib.auth.models import User
from django.utils import timezone

from .common import api_v1_site, format_authorization
from .exceptions import NotFoundError, InvalidParametersError
from apps.billing.models import Authorization
from utils.auth.backends import RADIUS_BACKEND_NAME
from utils.auth.decorators import manager_required


@jsonrpc_method('authorization.list(radius_username=String) -> Array',
                site=api_v1_site, authenticated=True, safe=True)
@manager_required
def authorization_list(request, radius_username=None):
    """
    Retrieve registered authorizations for the current selected organization.

    Required user level: Manager

    Provide radius_username to select only authorizations of the provided user.

    Returns an array of accounts of registered authorizations.

    radius_username    -- (optional) RADIUS username to search for.

    Example return value:
    [
        {
            "account": "NL13TEST0123456789",
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00",
            "user": "s0000000"
        }
    ]

    Raises error -32602 (Invalid params) if the radius_username does not exist.
    """

    result = []
    authorizations = Authorization.objects.filter(organization=request.organization)

    if radius_username is not None:
        try:
            user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except User.DoesNotExist:
            raise InvalidParametersError('User with provided radius_username does not exits')

        authorizations = authorizations.filter(user=user)

    authorizations = authorizations.select_related('user')

    for authorization in authorizations:
        result.append(format_authorization(authorization))

    return result


@jsonrpc_method('authorization.get(radius_username=String) -> Array',
                site=api_v1_site, authenticated=True, safe=True)
@manager_required
def authorization_get(request, radius_username):
    """
    ***DEPRECATED***
    Retrieve registered authorizations for a specified user and current selected
    organization.

    Required user level: Manager

    Returns an array of accounts of registered authorizations.

    radius_username    -- RADIUS username to search for.

    Example return value:
    [
        {
            "account": "NL13TEST0123456789",
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00"
        }
    ]
    """

    result = []
    authorizations = Authorization.objects.filter(user__authenticationdata__backend=RADIUS_BACKEND_NAME,
                                                  user__authenticationdata__username=radius_username,
                                                  organization=request.organization)

    for authorization in authorizations:
        result.append({
            'id': authorization.pk,
            'start_date': authorization.start_date.isoformat(),
            'end_date': authorization.end_date.isoformat() if authorization.end_date else None,
            'account': authorization.account,
        })

    return result


@jsonrpc_method('authorization.add(radius_username=String, account=String) -> Object',
                site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def authorization_add(request, radius_username, account):
    """
    Add a new authorization to the specified user.

    Required user level: Manager

    Returns the authorization on success.

    radius_username    -- RADIUS username to search for.
    account            -- Bank account number.

    Example return value:
    {
        "account": "NL13TEST0123456789",
        "id": 1,
        "end_date": null,
        "start_date": "2014-09-21T14:16:06+00:00",
        "user": "s0000000"
    }

    Raises error -32602 (Invalid params) if the radius_username does not exist.
    """

    try:
        user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParametersError('User with provided radius_username does not exits')

    authorization = Authorization(user=user, organization=request.organization, account=account)
    authorization.save()

    return format_authorization(authorization)


@jsonrpc_method('authorization.end(radius_username=String, authorization_id=Number) -> Boolean',
                site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def authorization_end(request, radius_username, authorization_id):
    """
    End an authorization from the specified user.

    Required user level: Manager

    Returns true when successful. Returns false when the authorization was already ended.

    radius_username    -- RADIUS username to search for.
    identifier         -- RFID card hardware identiefier (max. 16 chars)

    Raises error 404 if provided authorization cannot be found.
    """

    try:
        authorization = Authorization.objects.select_for_update().get(user__authenticationdata__backend=RADIUS_BACKEND_NAME,
                                                                      user__authenticationdata__username=radius_username,
                                                                      organization=request.organization,
                                                                      pk=authorization_id)
    except Authorization.DoesNotExist:
        raise NotFoundError

    if not authorization.end_date:
        authorization.end_date = timezone.now()
        authorization.save()
        return True
    else:
        return False
