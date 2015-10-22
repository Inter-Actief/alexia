from datetime import timedelta, datetime

from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from jsonrpc import jsonrpc_method

from .common import api_v1_site, format_event_extended
from apps.organization.models import Location, Organization
from apps.scheduling.models import Event, StandardReservation


@jsonrpc_method('event.list(String, String, String, String, Boolean, Array) -> Array', site=api_v1_site, safe=True, authenticated=True)
def event_list(request, start_date, start_time, end_date, end_time, only_unsynchronized=False, organizations=None):
    """Returns all events in the specified time span"""

    start = datetime.strptime("%s %s" % (start_date, start_time), "%Y-%m-%d %H:%M")
    end = datetime.strptime("%s %s" % (end_date, end_time), "%Y-%m-%d %H:%M")

    events = Event.objects.filter(starts_at__gte=start, ends_at__lte=end)

    organizations_objects = Organization.objects.filter(slug__in=organizations) if organizations is not None else None
    if organizations is not None:
        events = events.filter(organizer__in=organizations_objects)

    if only_unsynchronized:
        if organizations is None:
            raise NotImplementedError("Please specify organizations when requesting unsynchronized events")
        for organization in organizations_objects:
            if not request.user.profile.is_manager(organization):
                raise PermissionDenied

        events = events.filter(orders__synchronized=0).distinct()

    events.select_related('organizer').prefetch_related('participants', 'location')
    return [format_event_extended(event) for event in events]


@jsonrpc_method('event.adjecents(String, String, String, String, Number, Array) -> Array', site=api_v1_site,
                authenticated=True)
def event_adjecents(request, start_date, start_time, end_date, end_time, event=None, locations=None):
    """Returns the events which take place adjacent to the to-be-planned event."""

    start = datetime.strptime("%s %s" % (start_date, start_time), "%d-%m-%Y %H:%M") - timedelta(minutes=15)
    end = datetime.strptime("%s %s" % (end_date, end_time), "%d-%m-%Y %H:%M") + timedelta(minutes=15)
    realstart = datetime.strptime("%s %s" % (start_date, start_time), "%d-%m-%Y %H:%M")
    realend = datetime.strptime("%s %s" % (end_date, end_time), "%d-%m-%Y %H:%M")

    # Haal alle conflicting events op met een kwartier speling aan beide
    # einden. Haal vervolgens de de echte conflicting events eruit, zodat de
    # adjacent events overblijven.
    if locations:
        locations = Location.objects.filter(pk__in=locations)
        events = Event.objects.none()
        adjevents = Event.objects.none()
        for location in locations:
            events |= Event.conflicting_events(realstart, realend, location)
            adjevents |= Event.conflicting_events(start, end, location)
    else:
        events = Event.conflicting_events(realstart, realend)
        adjevents = Event.conflicting_events(start, end)

    if event:
        events = events.exclude(pk=event)

    result = []
    for event in adjevents:
        if event not in events:
            result.append(model_to_dict(event))

    return result


@jsonrpc_method('event.conflicts(String, String, String, String, Number, Array) -> Array', site=api_v1_site,
                authenticated=True)
def event_conflicts(request, start_date, start_time, end_date, end_time, event_id=None, locations=None):
    """Returns the events which take place at the same time as the to-be-planned event."""

    start = datetime.strptime("%s %s" % (start_date, start_time), "%d-%m-%Y %H:%M")
    end = datetime.strptime("%s %s" % (end_date, end_time), "%d-%m-%Y %H:%M")

    if locations:
        locations = Location.objects.filter(pk__in=locations.split(','))
        events = Event.objects.none()
        for location in locations:
            events |= Event.conflicting_events(start, end, location)
    else:
        events = Event.conflicting_events(start, end)

    if event_id:
        events = events.exclude(pk=event_id)

    result = []
    for event in events:
        result.append(model_to_dict(event))

    return result


@jsonrpc_method('event.conflicts_standard(String, String, String, String, Array) -> Array', site=api_v1_site,
                authenticated=True)
def event_conflicts_standard(request, start_date, start_time, end_date, end_time, locations=None):
    """Returns the standard reservations which are booked at the same time as the to-be-planned event."""

    start = datetime.strptime("%s %s" % (start_date, start_time), "%d-%m-%Y %H:%M")
    end = datetime.strptime("%s %s" % (end_date, end_time), "%d-%m-%Y %H:%M")
    s_reservations = StandardReservation.objects.occuring_at(start, end)

    if locations:
        locations = Location.objects.filter(pk__in=locations.split(','))
        s_reservations = s_reservations.filter(location__in=locations)

    result = []
    for event in s_reservations:
        result.append(model_to_dict(event))

    return result
