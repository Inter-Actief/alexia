from jsonrpc.site import JSONRPCSite

api_v1_site = JSONRPCSite()
api_v1_site.name = 'Alexia API v1'


def format_authorization(authorization):
    return {
        'id': authorization.pk,
        'user': authorization.user.username,
        'start_date': authorization.start_date.isoformat(),
        'end_date': authorization.end_date.isoformat() if authorization.end_date else None,
        'account': authorization.account,
    }


def format_event(event):
    return {
        'id': event.pk,
        'name': event.name,
    }


def format_order(order):
    purchases = [{
        'product': {
            'id': p.product.pk,
            'name': p.product.name,
        },
        'amount': p.amount,
        'price': p.price,
    } for p in order.purchases.all()]

    rfid = None
    if order.rfidcard:
        rfid = {
            'atqa': order.rfidcard.atqa if len(order.rfidcard.atqa) > 0 else None,
            'sak': order.rfidcard.sak if len(order.rfidcard.sak) > 0 else None,
            'uid': order.rfidcard.uid
        }

    return {
        'id': order.pk,
        'rfid': rfid,
        'event': format_event(order.event),
        'authorization': format_authorization(order.authorization),
        'placed_at': order.placed_at.isoformat(),
        'synchronized': order.synchronized,
        'purchases': purchases,
    }


def format_rfidcard(rfidcard):
    """

    :type rfidcard: apps.billing.models.RfidCard
    """
    return {
        'atqa': rfidcard.atqa if len(rfidcard.atqa) > 0 else None,
        'sak': rfidcard.sak if len(rfidcard.sak) > 0 else None,
        'uid': rfidcard.uid,
        'registered_at': rfidcard.registered_at.isoformat(),
        'user': rfidcard.user.username,
    }


def format_user(user):
    """

    :type user: django.contrib.auth.models.User
    """
    return {
        'radius_username': user.profile.radius_username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
