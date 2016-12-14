from datetime import timedelta, datetime

from django.forms.models import model_to_dict
from jsonrpc import jsonrpc_method

from alexia.apps.organization.models import Location
from alexia.apps.scheduling.models import Event, StandardReservation
from .common import api_v1_site


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
