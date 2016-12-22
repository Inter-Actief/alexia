import datetime
import json

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from alexia.apps.organization.models import Location
from alexia.auth.decorators import tender_required

from .models import Availability, Event


@tender_required
def bartender(request):
    events = Event.objects.filter(ends_at__gte=timezone.now(),
                                  bartender_availabilities__availability__nature=Availability.ASSIGNED,
                                  bartender_availabilities__user=request.user).order_by('starts_at')

    return render(request, 'scheduling/overview_bartender.html', locals())


def calendar(request):
    is_planner = request.user.is_authenticated() and request.organization and request.user.profile.is_planner(
        request.organization)
    return render(request, 'scheduling/overview_calendar.html', locals())


def calendar_fetch(request):
    if not request.is_ajax():
        return redirect(calendar)

    tz = timezone.get_current_timezone()
    from_time = datetime.datetime.fromtimestamp(float(request.GET.get('start')))
    till_time = datetime.datetime.fromtimestamp(float(request.GET.get('end')))
    data = []

    for event in Event.objects.filter(ends_at__gte=from_time,
                                      starts_at__lte=till_time).prefetch_related('location'):
        # Default color
        color = '#888888'

        try:
            location = event.location.get()
            if location.color:
                color = '#{}'.format(location.color)
        except Location.DoesNotExist:
            # No location, use default color
            pass
        except Location.MultipleObjectsReturned:
            # Multiple locations, use default color
            pass

        data.append({
            'title': event.name,
            'start': event.starts_at.astimezone(tz).isoformat(),
            'end': event.ends_at.astimezone(tz).isoformat(),
            'color': color,
            'organizers': ', '.join(map(lambda x: x.name,
                                        event.participants.all())),
            'location': ', '.join(map(lambda x: x.name, event.location.all())),
            'tenders': ', '.join(map(lambda x: x.first_name,
                                     event.get_assigned_bartenders())) or '<i>geen</i>',
        })

    return HttpResponse(json.dumps(data), content_type='application/json')
