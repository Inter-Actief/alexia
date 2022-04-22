from django.utils import timezone
from jsonrpc import jsonrpc_method

from alexia.apps.scheduling.models import Event

from ..config import api_v1_site


@jsonrpc_method('event.upcoming_list(include_ongoing=Boolean) -> Array', site=api_v1_site, safe=True)
def upcoming_events_list(request, include_ongoing=False):
    """
    List all current and upcoming events.

    Required user level: None

    include_current -- Whether to include ongoing events, defaults to false

    Returns an array with zero or more events.

    Example output:
    [{
        'name': 'Test Drink',
        'locations': 'Abscint',
        'organizer': 'Inter-Actief',
        'participants': ['Inter-Actief'],
        'starts_at': 2017-09-12T14:00:00Z,
        'ends_at': 2017-09-12T16:00:00Z,
        'kegs': 2,
        'is_risky': false,
    }]
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