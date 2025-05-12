from typing import List, Dict

from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import manager_required
from alexia.api.exceptions import InvalidParamsError
from alexia.apps.scheduling.models import BartenderAvailability
from alexia.auth.backends import OIDC_BACKEND_NAME, User


@rpc_method(name='user.get_availabilities', entry_point='v1')
@manager_required
def user_get_availabilities(radius_username: str, **kwargs) -> List[Dict]:
    """
    Retrieve the availabilities entered by a specific user for the current organization.

    Required user level: Manager

    radius_username     -- Username to search for.

    Raises error -32602 (Invalid params) if the username does not exist.

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
    request = kwargs.get(REQUEST_KEY)
    try:
        user = User.objects.get(authenticationdata__backend=OIDC_BACKEND_NAME,
                                authenticationdata__username=radius_username)
    except User.DoesNotExist:
        raise InvalidParamsError('User with provided username does not exits')

    availabilities = BartenderAvailability.objects.filter(user=user, event__organizer=request.organization)

    return [{
        "event": {
            "name": availability.event.name,
            "date": availability.event.starts_at
        },
        "availability": availability.availability.name
    } for availability in availabilities]
