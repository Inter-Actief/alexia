from typing import List, Dict, Optional

from django.contrib.auth.models import User
from django.db import transaction
from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError, ObjectNotFoundError
from alexia.apps.billing.models import Order
from alexia.auth.backends import OIDC_BACKEND_NAME

from ..common import format_order


@rpc_method(name='order.unsynchronized', entry_point='v1')
@manager_required
def order_unsynchronized(unused: int = 0, **kwargs) -> List[Dict]:
    """
    **Signature**: `order.unsynchronized(unused)`

    **Arguments**:

    - `unused` : `int` -- Unused parameter

    **Return type**: List of `dict`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Return a list of unsynchronized orders.

    Optionally gets an unused parameter because of a former compatibility issue
    between the jsonrpc server en jsonrpclib client.

    Returns a list of Order objects.

    **Example return value**:

        [
          {
            "purchases": [
                {
                    "price": "5.00",
                    "product": {"name": "Grolsch"},
                    "amount": 10
                },
                {
                    "price": "1.00",
                    "product": {"name": "Coca-Cola"},
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
                    "product": {"name": "Coca-Cola"},
                    "amount": 2
                }, {
                    "price": "0.50",
                    "product": {"name": "Grolsch"},
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
                "id": 1,
                "end_date": null,
                "start_date": "2014-09-21T14:16:06+00:00",
                "user": "s0000000"
            }
          }
        ]
    """
    request = kwargs.get(REQUEST_KEY)
    result = []
    orders = Order.objects.filter(authorization__organization=request.organization, synchronized=False)

    orders = orders.select_related('authorization__user', 'event')

    for order in orders:
        result.append(format_order(order))

    return result


@rpc_method(name='order.get', entry_point='v1')
@manager_required
def order_get(order_id: int, **kwargs) -> Dict:
    """
    **Signature**: `order.get(order_id)`

    **Arguments**:

    - `order_id` : `int` -- ID of the Order object.

    **Return type**: `dict`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Return a specific order.

    Returns an order object.

    **Example return value**:

        {
          "purchases": [
            {
              "price": "1.00",
              "product": {"name": "Coca-Cola"},
              "amount": 2
            }, {
              "price": "0.50",
              "product": {"name": "Grolsch"},
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
            "id": 1,
            "end_date": null,
            "start_date": "2014-09-21T14:16:06+00:00",
            "user": "s0000000"
          }
        }

    **Raises errors**:

    - `404` (Object not found) if provided order id cannot be found.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        order = Order.objects.get(authorization__organization=request.organization, pk=order_id)
    except Order.DoesNotExist:
        raise ObjectNotFoundError

    return format_order(order)


@rpc_method(name='order.list', entry_point='v1')
@manager_required
def order_list(radius_username: Optional[str] = None, **kwargs) -> List[Dict]:
    """
    **Signature**: `order.list(radius_username)`

    **Arguments**:

    - `radius_username` : `str` -- *(optional)* Username to search for.

    **Return type**: List of `dict`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Retrieve a list of orders for the currently selected organization.

    Provide a username to select only orders made by the provided user.

    Returns an array of orders.

    **Example return value**:

        [
          {
            "purchases": [
              {
                "price": "1.00",
                "product": {"name": "Coca-Cola"},
                "amount": 2
              }, {
                "price": "0.50",
                "product": {"name": "Grolsch"},
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
              "id": 1,
              "end_date": null,
              "start_date": "2014-09-21T14:16:06+00:00",
              "user": "s0000000"
            }
          },
          {
            "purchases": [
              {
                "price": "1.50",
                "product": {"name": "Grolsch"},
                "amount": 3
              }
            ],
            "synchronized": true,
            "event": {
              "id": 4210,
              "name": "Testborrel"
            },
            "placed_at": "2015-03-11T16:47:21+00:00",
            "id": 1271,
            "rfid": "02,06:65:74:49",
            "authorization": {
              "id": 1,
              "end_date": null,
              "start_date": "2014-09-21T14:16:06+00:00",
              "user": "s0000000"
            }
          }
        ]
    """
    request = kwargs.get(REQUEST_KEY)
    result = []
    orders = Order.objects.filter(event__organizer=request.organization)

    if radius_username is not None:
        try:
            user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                    authenticationdata__username=radius_username)
        except User.DoesNotExist:
            return []
        orders = orders.filter(authorization__user=user)

    orders = orders.select_related('event', 'authorization')

    for order in orders:
        result.append(format_order(order))

    return result


@rpc_method(name='order.marksynchronized', entry_point='v1')
@manager_required
@transaction.atomic
def order_marksynchronized(order_id: int, **kwargs) -> bool:
    """
    **Signature**: `order.marksynchronized(order_id)`

    **Arguments**:

    - `order_id` : `int` -- ID of the Order object.

    **Return type**: `bool`

    **Idempotent**: no

    **Required user level**: Manager

    **Documentation**:

    Mark an order as synchronized.

    Returns `True` if the operation succeeded. Returns `False` if the order is already marked as synchronized.

    **Raises errors**:

    - `-32602` (Invalid params) if provided order id cannot be found.
    """
    request = kwargs.get(REQUEST_KEY)
    try:
        order = Order.objects.select_for_update().get(authorization__organization=request.organization, pk=order_id)
    except Order.DoesNotExist:
        raise InvalidParamsError('Order with id not found')

    if not order.synchronized:
        order.synchronized = True
        order.save()
        return True
    else:
        return False
