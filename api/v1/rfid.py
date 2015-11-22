from django.db import transaction
from jsonrpc import jsonrpc_method
from django.contrib.auth.models import User

from .common import api_v1_site, format_rfidcard
from .exceptions import NotFoundError, InvalidParametersError
from apps.billing.models import RfidCard
from utils.auth.decorators import manager_required


@jsonrpc_method('rfid.list(radius_username=String) -> Array', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def rfid_list(request, radius_username=None):
    """
    Retrieve registered RFID cards for the current selected organization.

    Required user level: Manager

    Provide radius_username to select only RFID cards registered by the provided user.

    Returns an array of registered RFID cards.

    radius_username    -- (optional) RADIUS username to search for.

    Example return value:
    [
        {
            "atqa": "0004",
            "sak": "08",
            "uid": "98765432",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000000"
        },
        {
            "atqa": None,
            "sak": "00",
            "uid": "0123456789abcd",
            "registered_at": "2014-09-21T14:16:06+00:00"
            "user": "s0000019"
        }
    ]
    """

    result = []
    rfidcards = RfidCard.objects.filter(managed_by=request.organization)

    if radius_username is not None:
        rfidcards = rfidcards.filter(user__profile__radius_username=radius_username)

    rfidcards = rfidcards.select_related('user')

    for rfidcard in rfidcards:
        result.append(format_rfidcard(rfidcard))

    return result


@jsonrpc_method('rfid.add(radius_username=String, atqa=String, sak=String, uid=String) -> Object', site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def rfid_add(request, radius_username, atqa, sak, uid):
    """
    Add a new RFID card to the specified user.

    Required user level: Manager

    Returns the RFID card on success.

    radius_username    -- RADIUS username to search for.
    atqa               -- ATQA of the card (hexadecimal lowercase string, no colons, may be empty as a wildcard)
    sak                -- SAK of the card (hexadecimal lowercase string, no colons, may be empty as a wildcard)
    uid                -- UID of the card (hexadecimal lowercase string, no colons)

    Example return value:
    {
        "atqa": "0004",
        "sak": "08",
        "uid": "98765432",
        "registered_at": "2014-09-21T14:16:06+00:00"
        "user": "s0000000"
    }

    Raises error -32602 (Invalid params) if the radius_username does not exist.
    Raises error -32602 (Invalid params) if the RFID card already exists for this person.
    Raises error -32602 (Invalid params) if the RFID card is already registered by someone else.
    """

    try:
        user = User.objects.select_for_update().get(profile__radius_username=radius_username)
    except User.DoesNotExist:
        raise InvalidParametersError('User with provided radius_username does not exits')

    try:
        rfidcard = RfidCard.objects.select_for_update().get(user=user, atqa=atqa, sak=sak, uid=uid)
    except RfidCard.DoesNotExist:
        if RfidCard.objects.select_for_update().filter(atqa=atqa, sak=sak, uid=uid).exists():
            raise InvalidParametersError('RFID card already registered by someone else')

        rfidcard = RfidCard(user=user, atqa=atqa, sak=sak, uid=uid, is_active=True)
        rfidcard.save()

    if request.organization not in rfidcard.managed_by.all().select_for_update():
        rfidcard.managed_by.add(request.organization)
        rfidcard.save()
        return format_rfidcard(rfidcard)
    else:
        raise InvalidParametersError('RFID card already exists for this person')


@jsonrpc_method('rfid.remove(radius_username=String, atqa=String, sak=String, uid=String) -> Nil',
                site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def rfid_remove(request, radius_username, atqa, sak, uid):
    """
    Remove a RFID card from the specified user.

    Required user level: Manager

    radius_username    -- RADIUS username to search for.
    atqa               -- ATQA of the card (hexadecimal lowercase string, no colons)
    sak                -- SAK of the card (hexadecimal lowercase string, no colons)
    uid                -- UID of the card (hexadecimal lowercase string, no colons)

    Raises error 404 if provided order id cannot be found.
    """

    try:
        rfidcard = RfidCard.objects.select_for_update().get(user__profile__radius_username=radius_username,
                                                            atqa=atqa, sak=sak, uid=uid)
    except RfidCard.DoesNotExist:
        raise NotFoundError

    managed_by = rfidcard.managed_by.all().select_for_update()

    if request.organization not in managed_by:
        # This RFID card does not exist in this organization
        raise NotFoundError

    if len(managed_by) == 1:
        # Only this organization left
        rfidcard.delete()
    else:
        rfidcard.managed_by.remove(request.organization)
