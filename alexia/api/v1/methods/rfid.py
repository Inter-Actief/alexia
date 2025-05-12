from typing import List, Dict

from django.contrib.auth.models import User
from django.db import transaction
from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError
from alexia.apps.billing.models import RfidCard
from alexia.auth.backends import OIDC_BACKEND_NAME

from ..common import format_rfidcard


@rpc_method(name='rfid.list', entry_point='v1')
@manager_required
def rfid_list(radius_username: str = None, **kwargs) -> List[Dict]:
    """
    Retrieve registered RFID cards for the current selected organization.

    Required user level: Manager

    Provide radius_username to select only RFID cards registered by the provided user.

    Returns an array of registered RFID cards.

    radius_username    -- (optional) Username to search for.

    Example return value:
    [
        {
            "identifier": "02,98:76:54:32",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000000"
        },
        {
            "identifier": "02,dd:ee:ff:00",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000000"
        },
        {
            "identifier": "03,fe:dc:ba:98",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000000"
        },
        {
            "identifier": "05,01:23:45:67:89:ab:cd",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000019"
        }
    ]
    """
    request = kwargs.get(REQUEST_KEY)
    result = []
    rfidcards = RfidCard.objects.filter(managed_by=request.organization)

    if radius_username is not None:
        try:
            user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except User.DoesNotExist:
            return []
        rfidcards = rfidcards.filter(user=user)

    rfidcards = rfidcards.select_related('user')

    for rfidcard in rfidcards:
        result.append(format_rfidcard(rfidcard))

    return result


@rpc_method(name='rfid.get', entry_point='v1')
@manager_required
def rfid_get(radius_username: str, **kwargs) -> List[str]:
    """
    Retrieve registered RFID cards for a specified user and current selected
    organization.

    Required user level: Manager

    Returns an array of registered RFID cards.

    radius_username    -- Username to search for.

    Example return value:
    [
        "02,98:76:54:32",
        "02,dd:ee:ff:00",
        "03,fe:dc:ba:98",
        "05,01:23:45:67:89:ab:cd"
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

    rfidcards = RfidCard.objects.filter(user=user, managed_by=request.organization)

    for rfidcard in rfidcards:
        result.append(rfidcard.identifier)

    return result


@rpc_method(name='rfid.add', entry_point='v1')
@manager_required
@transaction.atomic
def rfid_add(radius_username: str, identifier: str, **kwargs) -> Dict:
    """
    Add a new RFID card to the specified user.

    Required user level: Manager

    Returns the RFID card on success.

    radius_username    -- Username to search for.
    identifier         -- RFID card hardware identiefier.

    Example return value:
    {
        "identifier": "02,98:76:54:32",
        "registered_at": "2014-09-21T14:16:06+00:00"
        "user": "s0000000"
    }

    Raises error -32602 (Invalid params) if the username does not exist.
    Raises error -32602 (Invalid params) if the RFID card already exists for this person.
    Raises error -32602 (Invalid params) if the RFID card is already registered by someone else.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    try:
        rfidcard = RfidCard.objects.select_for_update().get(user=user, identifier=identifier)
    except RfidCard.DoesNotExist:
        if RfidCard.objects.select_for_update().filter(identifier=identifier).exists():
            raise InvalidParamsError('RFID card with provided identifier already registered by someone else')

        rfidcard = RfidCard(user=user, identifier=identifier, is_active=True)
        rfidcard.save()

    if request.organization not in rfidcard.managed_by.all().select_for_update():
        rfidcard.managed_by.add(request.organization)
        rfidcard.save()
        return format_rfidcard(rfidcard)
    else:
        raise InvalidParamsError('RFID card with provided identifier already exists for this person')


@rpc_method(name='rfid.remove', entry_point='v1')
@manager_required
@transaction.atomic
def rfid_remove(radius_username: str, identifier: str, **kwargs) -> None:
    """
    Remove an RFID card from the specified user.

    Required user level: Manager

    radius_username    -- Username to search for.
    identifier         -- RFID card hardware identiefier.

    Raises error -32602 (Invalid params) if the username does not exist.
    Raises error -32602 (Invalid params) if the RFID card does not exist for this person/organization.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    try:
        rfidcard = RfidCard.objects.select_for_update().get(user=user, identifier=identifier)
    except RfidCard.DoesNotExist:
        raise InvalidParamsError('RFID card not found')

    managed_by = rfidcard.managed_by.all().select_for_update()

    if request.organization not in managed_by:
        # This RFID card does not exist in this organization
        raise InvalidParamsError('RFID card not found')

    if len(managed_by) == 1:
        # Only this organization left
        rfidcard.delete()
    else:
        rfidcard.managed_by.remove(request.organization)
