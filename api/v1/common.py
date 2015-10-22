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


def format_location(location):
    """
    :type location: apps.organization.models.Location
    """
    return {
        'id': location.pk,
        'name': location.name
    }


def format_event(event):
    """
    :type event: apps.scheduling.models.Event
    """
    return {
        'id': event.pk,
        'name': event.name
    }


def format_event_extended(event):
    """
    :type event: apps.scheduling.models.Event
    """
    return {
        'id': event.pk,
        'name': event.name,
        'organizer': format_organization(event.organizer),
        'participants': [format_organization(x) for x in event.participants.all()],
        'locations': [format_location(x) for x in event.location.all()],
        'starts_at': event.starts_at.isoformat(),
        'ends_at': event.ends_at.isoformat()
    }



def format_organization(organization):
    """
    :type organization: apps.organization.models.Organization
    """
    return {
        'slug': organization.slug,
        'name': organization.name
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
    return {
        'radius_username': user.profile.radius_username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
