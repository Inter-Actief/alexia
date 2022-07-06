from django.contrib.auth.models import User
from django.db import transaction
from jsonrpc import jsonrpc_method

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError
from alexia.apps.billing.models import RfidCard
from alexia.auth.backends import RADIUS_BACKEND_NAME, SAML2_BACKEND_NAME

from ..common import format_rfidcard
from ..config import api_v1_site


@jsonrpc_method('rfid.list(radius_username=String) -> Array', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def rfid_list(request, radius_username=None):
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
    result = []
    rfidcards = RfidCard.objects.filter(managed_by=request.organization)

    if radius_username is not None:
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
                    return []
        rfidcards = rfidcards.filter(user=user)

    rfidcards = rfidcards.select_related('user')

    for rfidcard in rfidcards:
        result.append(format_rfidcard(rfidcard))

    return result


@jsonrpc_method('rfid.get(radius_username=String) -> Array', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def rfid_get(request, radius_username):
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
    result = []
    get_user_by_username(radius_username)

    rfidcards = RfidCard.objects.filter(user=user, managed_by=request.organization)

    for rfidcard in rfidcards:
        result.append(rfidcard.identifier)

    return result


@jsonrpc_method('rfid.add(radius_username=String, identifier=String) -> Object', site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic
def rfid_add(request, radius_username, identifier):
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

    get_user_by_username(radius_username)

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


@jsonrpc_method('rfid.remove(radius_username=String, identifier=String) -> Nil', site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic
def rfid_remove(request, radius_username, identifier):
    """
    Remove a RFID card from the specified user.

    Required user level: Manager

    radius_username    -- Username to search for.
    identifier         -- RFID card hardware identiefier.

    Raises error -32602 (Invalid params) if the username does not exist.
    Raises error -32602 (Invalid params) if the RFID card does not exist for this person/organization.
    """
    user = get_user_by_username(radius_username)

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
