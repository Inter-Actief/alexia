import base64

from alexia.apps.organization.models import AuthenticationData, Certificate
from alexia.auth.backends import RADIUS_BACKEND_NAME


def format_authorization(authorization):
    return {
        'id': authorization.pk,
        'user': authorization.user.username,
        'user_id': authorization.user.id,
        'start_date': authorization.start_date.isoformat(),
        'end_date': authorization.end_date.isoformat() if authorization.end_date else None,
    }


def format_event(event):
    return {
        'id': event.pk,
        'name': event.name,
    }


def format_order(order):
    purchases = [{
        'product': {
            'id': -1,
            'name': p.product,
        },
        'amount': p.amount,
        'price': p.price,
    } for p in order.purchases.all()]

    return {
        'id': order.pk,
        'rfid': order.rfidcard.identifier if order.rfidcard else None,
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
        'identifier': rfidcard.identifier,
        'registered_at': rfidcard.registered_at.isoformat(),
        'user': rfidcard.user.username,
    }


def format_user(user):
    """

    :type user: django.contrib.auth.models.User
    """
    try:
        user_name = user.authenticationdata_set.get(backend=RADIUS_BACKEND_NAME).username
    except AuthenticationData.DoesNotExist:
        user_name = None

    auth_data = [{
        'backend': u.backend,
        'username': u.username,
    } for u in user.authenticationdata_set.all()]

    return {
        'id': user.id,
        'radius_username': user_name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'authentication_data': auth_data
    }


def format_certificate(certificate):
    """

    :type certificate: alexia.apps.organization.models.Certificate
    """
    with open(certificate.file.path, "rb") as certificate_file:
        certificate_b64 = base64.b64encode(certificate_file.read())

    return {
        'user': certificate.owner.username,
        'certificate_data': certificate_b64.decode("utf-8")
    }
