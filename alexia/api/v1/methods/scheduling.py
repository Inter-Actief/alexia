from jsonrpc import jsonrpc_method

from alexia.api.decorators import manager_required
from alexia.api.exceptions import ObjectNotFoundError
from alexia.apps.scheduling.models import BartenderAvailability
from alexia.auth.backends import User, RADIUS_BACKEND_NAME

from ..config import api_v1_site


@jsonrpc_method('user.get_availabilities(radius_username=String) -> Array', site=api_v1_site, safe=True, authenticated=True)
@manager_required
def user_get_availabilities(request, radius_username):
    """
    Retrieve the availabilities entered by a specific user for the current organization.

    Required user level: Manager

    radius_username     -- RADIUS username to search for.

    Raises error 404 if the specified user does not exist.

    Example result value:
    [
        {
            "event": {
                "name": "Test Drink",
                "date": "2017-09-12T14:00:00Z",

            },
            "availability": "Yes"
        },
        {
            "event": {
                "name": "Test Drink 2",
                "date": "2017-09-18T16:00:00Z",

            },
            "availability": "Maybe"
        }
    ]
    """
    try:
        user = User.objects.get(authenticationdata__backend=RADIUS_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise ObjectNotFoundError

    availabilities = BartenderAvailability.objects.filter(user=user, event__organizer=request.organization)

    return [{
        "event": {
            "name": availability.event.name,
            "date": availability.event.starts_at
        },
        "availability": availability.availability.name
    } for availability in availabilities]
