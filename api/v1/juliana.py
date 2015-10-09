from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from jsonrpc import jsonrpc_method
from jsonrpc.exceptions import InvalidParamsError, OtherError

from .common import api_v1_site, format_authorization
from apps.scheduling.models import Event
from apps.billing.models import Order, Purchase, RfidCard, Authorization, Product
from .exceptions import ForbiddenError

def rfid_to_identifier(rfid):
    if 'atqa' not in rfid:
        raise InvalidParamsError('atqa value required')
    if 'sak' not in rfid:
        raise InvalidParamsError('sak value required')
    if 'uid' not in rfid:
        raise InvalidParamsError('uid value required')

    if rfid['atqa'] == "00:04" and rfid['sak'] == "08":
        # MIFARE Classic 1k
        ia_rfid_prefix = '02'
    elif rfid['atqa'] == "00:02" and rfid['sak'] == "18":
        # MIFARE Classic 4k
        ia_rfid_prefix = '03'
    elif rfid['atqa'] == "03:44" and rfid['sak'] == "20":
        # MIFARE DESFire
        ia_rfid_prefix = '04'
    elif rfid['atqa'] == "00:44" and rfid['sak'] == "00":
        # MIFARE Ultralight
        ia_rfid_prefix = '05'
    else:
        raise InvalidParamsError('atqa/sak combination unknown')

    return '%s,%s' % (ia_rfid_prefix, rfid['uid'])

@jsonrpc_method('juliana.rfid.get(Number,Object) -> Object', site=api_v1_site, safe=True, authenticated=True)
def juliana_rfid_get(request, event_id, rfid):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise InvalidParamsError('Event does not exist')

    cur_user = request.user
    if not request.user.is_superuser and not event.is_tender(cur_user):
        raise ForbiddenError('Forbidden - You are not a tender for this event')
    if not request.user.is_superuser and not event.can_be_opened():
        raise ForbiddenError('Forbidden - This event is not open')

    identifier = rfid_to_identifier(rfid=rfid)

    try:
        card = RfidCard.objects.get(identifier=identifier, is_active=True)
    except RfidCard.DoesNotExist:
        raise InvalidParamsError('RFID card not found')

    user = card.user
    authorization = Authorization.get_for_user_event(user, event)

    if not authorization:
        raise InvalidParamsError('No authorization found for user')

    res = {
        'user': {
            'id': user.pk,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        },
        'authorization': format_authorization(authorization),
    }

    return res


@jsonrpc_method('juliana.order.save(Number,Number,Array,Object) -> Nil', site=api_v1_site, authenticated=True)
@transaction.atomic
def juliana_order_save(request, event_id, user_id, purchases, rfid_data):
    """Saves a new order in the database"""

    rfid_identifier = rfid_to_identifier(rfid=rfid_data)

    try:
        event = Event.objects.get(pk=event_id)
        user = User.objects.get(pk=user_id)
        rfidcard = RfidCard.objects.get(identifier=rfid_identifier, is_active=True)
    except Event.DoesNotExist:
        raise InvalidParamsError('Event does not exist')
    except User.DoesNotExist:
        raise InvalidParamsError('User does not exist')
    except RfidCard.DoesNotExist:
        raise InvalidParamsError('RFID card not found')

    cur_user = request.user
    if not request.user.is_superuser and not event.is_tender(cur_user):
        raise ForbiddenError('Forbidden - You are not a tender for this event')
    if not request.user.is_superuser and not event.can_be_opened():
        raise ForbiddenError('Forbidden - This event is not open')

    authorization = Authorization.get_for_user_event(user, event)

    if not authorization:
        raise InvalidParamsError('No authorization available')

    order = Order(event=event, authorization=authorization, added_by=cur_user, rfidcard=rfidcard)
    order.save()

    for p in purchases:
        if p['product'][0:7] != 'product':
            raise InvalidParamsError('Product %s invalid' % p['product'])

        product_pk = int(p['product'][7:])

        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            raise InvalidParamsError('Product %s not found' % p['product'])

        if product.is_permanent:
            product = product.permanentproduct
            if product.organization != event.organizer \
                    or product.productgroup not in event.pricegroup.productgroups.all():
                raise InvalidParamsError('Product %s is not available for this event' % p['product'])
        elif product.is_temporary:
            product = product.temporaryproduct
            if event != product.event:
                raise InvalidParamsError('Product %s is not available for this event' % p['product'])
        else:
            raise OtherError('Product %s is broken' % p['product'])

        amount = p['amount']

        if p['amount'] <= 0:
            raise InvalidParamsError('Zero or negative amount not allowed')

        price = amount * product.get_price(event)

        if price != p['price'] / Decimal(100):
            raise InvalidParamsError('Price for product %s is incorrect' % p['product'])

        purchase = Purchase(order=order, product=product, amount=amount, price=price)
        purchase.save()

    order.save(force_update=True)  # ensure order.amount is correct
    return True


@jsonrpc_method('juliana.user.check(Number, Number) -> Number', site=api_v1_site, safe=True, authenticated=True)
def juliana_user_check(request, event_id, user_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise InvalidParamsError('Event does not exist')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise InvalidParamsError('User does not exist')

    cur_user = request.user
    if not request.user.is_superuser and not event.is_tender(cur_user):
        raise ForbiddenError('Forbidden - You are not a tender for this event')
    if not request.user.is_superuser and not event.can_be_opened():
        raise ForbiddenError('Forbidden - This event is not open')

    order_sum = Order.objects \
        .filter(authorization__in=user.authorizations.all(), event=event) \
        .aggregate(Sum('amount'))['amount__sum']

    if order_sum:
        return int(order_sum * 100)
    else:
        return 0
