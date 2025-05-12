from typing import List, Dict

from django.utils import timezone
from modernrpc.core import rpc_method

from alexia.apps.scheduling.models import Event


@rpc_method(name='event.upcoming_list', entry_point='v1')
def upcoming_events_list(include_ongoing: bool = False, **kwargs) -> List[Dict]:
    """
    **Signature**: `event.upcoming_list(include_current)`

    **Arguments**:

    - `include_current` : `bool` -- Whether to include ongoing events, defaults to false

    **Return type**: List of `dict`

    **Idempotent**: yes

    **Required user level**: *None*

    **Documentation**:

    List all current and upcoming events.

    Returns an array with zero or more events.

    **Example return value**:

        [
          {
            'name': 'Test Drink',
            'locations': 'Abscint',
            'organizer': 'Inter-Actief',
            'participants': ['Inter-Actief'],
            'starts_at': 2017-09-12T14:00:00Z,
            'ends_at': 2017-09-12T16:00:00Z,
            'kegs': 2,
            'is_risky': false,
          }
        ]
    """
    filter_key = 'ends_at__gte' if include_ongoing else 'starts_at__gte'
    return [{
                'name': e.name,
                'locations': [l.name for l in e.location.all()],
                'organizer': e.organizer.name,
                'participants': [p.name for p in e.participants.all()],
                'starts_at': e.starts_at,
                'ends_at': e.ends_at,
                'kegs': e.kegs,
                'is_risky': e.is_risky,
            } for e in Event.objects.filter(**{filter_key: timezone.now()})]
