from datetime import datetime, timedelta
import json

from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import redirect, render

from apps.organization.models import Location
from utils.auth.decorators import tender_required
from .models import Event, Availability


@tender_required
def bartender(request):
    events = Event.objects.filter(ends_at__gte=timezone.now(),
                                  deleted=False,
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
    from_time = datetime.fromtimestamp(float(request.GET.get('start')))
    till_time = datetime.fromtimestamp(float(request.GET.get('end')))
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
            'id': event.pk,
            'title': event.name,
            'start': event.starts_at.astimezone(tz).isoformat(),
            'end': event.ends_at.astimezone(tz).isoformat(),
            'color': color,
            'organizers': ', '.join(map(lambda x: x.name,
                                        event.participants.all())),
            'location': ', '.join(map(lambda x: x.name, event.location.all())),
            'tenders': ', '.join(map(lambda x: x.first_name,
                                     event.get_assigned_bartenders())) or '<i>geen</i>',
            'canEdit': request.user.profile.is_planner(event.organizer) if hasattr(request.user, 'profile') else False,
            'editUrl': event.get_absolute_url()
        })

    return HttpResponse(json.dumps(data), content_type='application/json')


def ios(request):
    events = Event.objects.select_related().filter(starts_at__gte=timezone.now,
                                                   starts_at__lte=timezone.now() + timedelta(days=14)).order_by(
        'starts_at')
    events = events.distinct()
    return render(request, 'scheduling/overview_ios.html', locals())
