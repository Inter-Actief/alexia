from django.db import transaction
from jsonrpc import jsonrpc_method

from .common import api_v1_site, format_order
from .exceptions import NotFoundError
from apps.billing.models import Order
from utils.auth.decorators import manager_required


@jsonrpc_method('order.unsynchronized(unused=Number) -> Array', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def order_unsynchronized(request, unused=0):
    """
    Return a list of unsynchronized orders.

    Required user level: Manager

    Optionally gets an unused parameter because of a former compatibility issue
    between the jsonrpc server en jsonrpclib client.

    Returns a list of Order objects.

    Example return value:
    [
        {
            "purchases": [
                {
                    "price": "5.00",
                    "product": {"id": 1, "name": "Grolsch"},
                    "amount": 10
                },
                {
                    "price": "1.00",
                    "product": {"id": 2, "name": "Coca Cola"},
                    "amount": 2
                }
            ],
            "synchronized": false,
            "event": {
                "id": 4210,
                "name": "Testborrel"
            },
            "placed_at": "2015-03-11T15:13:55+00:00",
            "id": 1254,
            "rfid": "02,06:65:74:49",
            "authorization": {
                "account": "NL13TEST0123456789",
                "id": 1,
                "end_date": null,
                "start_date": "2014-09-21T14:16:06+00:00",
                "user": "s0000000"
            }
        },
        {
            "purchases": [
                {
                    "price": "1.00",
                    "product": {"id": 2, "name": "Coca Cola"},
                    "amount": 2
                }, {
                    "price": "0.50",
                    "product": {"id": 1, "name": "Grolsch"},
                    "amount": 1
                }
            ],
            "synchronized": false,
            "event": {
                "id": 4210,
                "name": "Testborrel"
            },
            "placed_at": "2015-03-11T15:24:06+00:00",
            "id": 1255,
            "rfid": "02,06:65:74:49",
            "authorization": {
                "account": "NL13TEST0123456789",
                "id": 1,
                "end_date": null,
                "start_date": "2014-09-21T14:16:06+00:00",
                "user": "s0000000"
            }
        }
    ]
    """
    result = []
    orders = Order.objects.filter(authorization__organization=request.organization, synchronized=False)

    orders = orders.select_related('authorization__user', 'event').prefetch_related('purchases__product')

    for order in orders:
        result.append(format_order(order))

    return result


@jsonrpc_method('order.get(order_id=Number) -> Object', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def order_get(request, order_id):
    """
    Return a specific order.

    Required user level: Manager

    Returns an order object.

    order_id -- ID of the Order object.

    Raises error 404 if provided order id cannot be found.

    Example return value:
    {
        "purchases": [
            {
                "price": "1.00",
                "product": {"id": 2, "name": "Coca Cola"},
                "amount": 2
            }, {
                "price": "0.50",
                "product": {"id": 1, "name": "Grolsch"},
                "amount": 1
            }
        ],
        "synchronized": false,
        "event": {
            "id": 4210,
            "name": "Testborrel"
        },
        "placed_at": "2015-03-11T15:24:06+00:00",
        "id": 1255,
        "rfid": "02,06:65:74:49",
        "authorization": {
            "account": "NL13TEST0123456789",
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00",
            "user": "s0000000"
        }
    }
    """
    try:
        order = Order.objects.get(authorization__organization=request.organization, pk=order_id)
    except Order.DoesNotExist:
        raise NotFoundError

    return format_order(order)


@jsonrpc_method('order.marksynchronized(order_id=Number) -> Boolean', site=api_v1_site, authenticated=True)
@manager_required
@transaction.atomic()
def order_marksynchronized(request, order_id):
    """
    Mark an order as synchronized.

    Required user level: Manager

    Returns True if the operation succeeded. Returns False if the order is already marked as synchronized.

    order_id -- ID of the Order object.

    Raises error 404 if provided order id cannot be found.
    """
    try:
        order = Order.objects.select_for_update().get(authorization__organization=request.organization, pk=order_id)
    except Order.DoesNotExist:
        raise NotFoundError

    if not order.synchronized:
        order.synchronized = True
        order.save()
        return True
    else:
        return False
