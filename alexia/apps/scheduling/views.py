from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from alexia.apps.organization.forms import BartenderAvailabilityForm
from alexia.apps.organization.models import Location, Membership, Profile
from alexia.auth.mixins import (
    DenyWrongOrganizationMixin, ManagerRequiredMixin, PlannerRequiredMixin,
    TenderRequiredMixin,
)
from alexia.forms import CrispyFormMixin
from alexia.http import IcalResponse
from alexia.utils import log
from alexia.utils.calendar import generate_ical
from alexia.views import (
    CreateViewForEvent, CreateViewForOrganization, OrganizationFilterMixin,
    OrganizationFormMixin,
)

from .forms import EventForm, FilterEventForm
from .models import Availability, BartenderAvailability, Event, MailTemplate


def event_list_view(request):
    # De lijst waarop we nog gaan filteren
    events = Event.objects.select_related().prefetch_related('participants', 'location').order_by('starts_at')
    events = events.prefetch_related(
        Prefetch(
            'bartender_availabilities',
            queryset=BartenderAvailability.objects.filter(availability__nature=Availability.ASSIGNED),
            to_attr='bartender_availabilities_assigned',
        ),
        'bartender_availabilities_assigned__user',
        Prefetch(
            'bartender_availabilities',
            queryset=BartenderAvailability.objects.filter(
                Q(availability__nature=Availability.ASSIGNED),
                Q(user__profile__is_iva=True) | Q(user__certificate__approved_at__isnull=False),
            ),
            to_attr='bartender_availabilities_iva',
        ),
    )

    # Default from_time is now.
    from_time = timezone.now()
    end_time = None

    # Filterformulier maken, al dan niet met huidige waarden
    if request.GET:
        filter_form = FilterEventForm(request.GET)

        if filter_form.is_valid():
            data = filter_form.cleaned_data

            if data['location']:
                events = events.filter(location__in=data['location'])

            if data['organizer']:
                events = events.filter(organizer=data['organizer'])

            if data['from_time']:
                from_time = data['from_time']

            if data['till_time']:
                end_time = data['till_time']

            if data['meetings_only']:
                events = events.filter(kegs=0)
    else:
        filter_form = FilterEventForm()

    events = events.filter(ends_at__gte=from_time)
    if end_time:
        events = events.filter(starts_at__lte=end_time)

    # Dubbele resultaten weghalen
    events = events.distinct()

    if request.user.is_authenticated():
        events_tending = events.filter(
            bartender_availabilities__availability__nature=Availability.ASSIGNED,
            bartender_availabilities__user=request.user,
        ).select_related(None).prefetch_related(None).order_by()

    # Beschikbaarheden in een lijstje stoppen
    if not request.user.is_authenticated() or not request.organization:
        availabilities = []
    elif request.user.is_superuser \
            or request.user.profile.is_planner(request.organization) \
            or not request.organization.assigns_tenders:
        availabilities = list(request.organization.availabilities.all())
    else:
        availabilities = list(request.organization.availabilities.exclude(nature=Availability.ASSIGNED))
    # Net als onze BartenderAvailabilities
    bartender_availabilities = BartenderAvailability.objects.filter(
        user_id=request.user.pk).values('event_id', 'availability_id')

    return render(request, 'scheduling/event_list.html', locals())


class EventBartenderView(TenderRequiredMixin, ListView):
    template_name_suffix = '_bartender'

    def get_queryset(self):
        return Event.objects.filter(
            ends_at__gte=timezone.now(),
            bartender_availabilities__availability__nature=Availability.ASSIGNED,
            bartender_availabilities__user=self.request.user
        ).order_by('starts_at')


class EventCalendarView(TemplateView):
    template_name = 'scheduling/event_calendar.html'


class EventCalendarFetch(View):
    def get(self, request, *args, **kwargs):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)

        if not (start and end) or not request.is_ajax():
            raise SuspiciousOperation('Bad calendar fetch request')

        from_time = datetime.fromtimestamp(float(start), tz=timezone.utc)
        till_time = datetime.fromtimestamp(float(end), tz=timezone.utc)

        data = []
        for event in Event.objects.filter(ends_at__gte=from_time,
                                          starts_at__lte=till_time).prefetch_related('location'):
            color = '#888888'
            try:
                location = event.location.get()
                color = '#' + location.color if location.color else color
            except Location.MultipleObjectsReturned:
                pass

            data.append({
                'title': event.name,
                'allDay': False,
                'start': event.starts_at.isoformat(),
                'end': event.ends_at.isoformat(),
                'color': color,
                'organizers': ', '.join(map(lambda x: x.name, event.participants.all())),
                'location': ', '.join(map(lambda x: x.name, event.location.all())),
                'tenders': ', '.join(map(lambda x: x.first_name, event.get_assigned_bartenders())) or '<i>geen</i>',
            })
        return JsonResponse(data, safe=False)


class EventMatrixView(TemplateView):
    template_name = 'scheduling/event_matrix.html'

    def get_context_data(self, **kwargs):
        events = self.get_events()

        context = super(EventMatrixView, self).get_context_data(**kwargs)
        context['events'] = events
        context['tenders'] = self.get_tenders(events)
        return context

    def get_events(self):
        return Event.objects.select_related().prefetch_related(
            Prefetch(
                'bartender_availabilities',
                queryset=BartenderAvailability.objects.select_related('user', 'event', 'availability')
            )
        ).filter(ends_at__gte=timezone.now(), participants=self.request.organization).order_by('starts_at')

    def get_tenders(self, events):
        tenders_list = Membership.objects.select_related('user').filter(
            organization=self.request.organization,
            is_tender=True,
            is_active=True
        ).order_by('user__first_name')

        tenders = []
        for tender in tenders_list:
            tender_availabilities = [
                next((a.availability for a in e.bartender_availabilities.all() if a.user == tender.user), None)
                for e in events
            ]
            tender_events = [
                {'event': event, 'availability': availability}
                for event, availability in zip(events, tender_availabilities)
            ]
            tended = [
                a.event
                for a in tender.tended() if a.event.starts_at < timezone.now()
            ]
            tenders.append({
                'tender': tender,
                'tended': len(tended),
                'last_tended': tended[0] if tended else None,
                'events': tender_events
            })
        return tenders


class EventDetailView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        if hasattr(self.request.user, 'profile') and self.request.user.profile.is_planner(self.object.organizer):
            context.update(self.get_tender_list())
        return context

    def get_tender_list(self):
        tenders = Membership.objects.select_related('user').filter(
            organization__in=self.object.participants.all(),
            is_tender=True,
        ).order_by('-is_active', 'user__first_name')

        bas = {}
        for ba in self.object.bartender_availabilities.all():
            bas[ba.user] = ba

        tender_list = []
        for tender in tenders:
            try:
                availability = bas[tender.user].availability
            except KeyError:
                availability = None

            tender_list.append({
                'tender': tender,
                'availability': availability,
                'last_tended': tender.last_tended()
            })
        return {'tender_list': tender_list}


class EventCreateView(PlannerRequiredMixin, OrganizationFormMixin, CrispyFormMixin, CreateViewForEvent):
    model = Event
    form_class = EventForm

    def get_initial(self):
        return {
            'participants': self.request.organization,
            'starts_at': parse_datetime(self.request.GET.get('starts_at', '')),
            'ends_at': parse_datetime(self.request.GET.get('ends_at', '')),
        }

    def form_valid(self, form):
        response = super(EventCreateView, self).form_valid(form)
        log.event_created(self.request.user, self.object)
        return response


class EventUpdateView(PlannerRequiredMixin, OrganizationFormMixin, DenyWrongOrganizationMixin, CrispyFormMixin,
                      UpdateView):
    model = Event
    form_class = EventForm
    organization_field = 'organizer'

    def form_valid(self, form):
        response = super(EventUpdateView, self).form_valid(form)
        log.event_modified(self.request.user, self.object)
        return response


@login_required
def event_edit_bartender_availability(request, pk, user_pk):
    if not request.user.is_authenticated() or not request.user.is_superuser and (
            not request.organization or not request.user.profile.is_planner(request.organization)):
        raise PermissionDenied

    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(User, pk=user_pk)

    if event.organizer != request.organization:
        raise PermissionDenied

    try:
        bartender_availability = BartenderAvailability.objects.get(event=event,
                                                                   user=user)
        old_availability = bartender_availability.availability
    except BartenderAvailability.DoesNotExist:
        bartender_availability = None
        old_availability = None

    if request.method == 'POST':
        form = BartenderAvailabilityForm(data=request.POST,
                                         instance=bartender_availability, event=event, user=user)
        if form.is_valid():
            if bartender_availability:
                form.save()
                log.availability_changed(
                    request.user, event, user, old_availability,
                    bartender_availability.availability)
            else:
                bartender_availability = form.save()
                log.availability_created(
                    request.user, event, user,
                    bartender_availability.availability)
            return redirect('event', pk=event.pk)
    else:
        form = BartenderAvailabilityForm(instance=bartender_availability,
                                         event=event, user=user)

    return render(request, 'scheduling/event_bartender_availability_form.html', locals())


class EventDelete(PlannerRequiredMixin, DenyWrongOrganizationMixin, DeleteView):
    model = Event
    organization_field = 'organizer'
    success_url = reverse_lazy('event-list')

    def get_success_url(self):
        log.event_deleted(self.request.user, self.object)
        return super(EventDelete, self).get_success_url()


@login_required
def set_bartender_availability(request):
    event = get_object_or_404(Event, pk=request.POST.get('event_id'))
    availability = get_object_or_404(
        Availability, pk=request.POST.get('availability_id'))

    if (request.organization not in event.participants.all()) or \
            not request.user.profile.is_tender(request.organization) or \
            event.is_closed:
        raise PermissionDenied

    # When the organizer assigns tenders, only planners and higher are allowed
    # to set availability to assigned.
    if event.organizer.assigns_tenders and \
            not request.user.is_superuser and \
            not request.user.profile.is_planner(event.organizer) and \
            availability.nature == Availability.ASSIGNED:
        raise PermissionDenied

    # And if you're already assigned, you can't change your own availability.
    if event.organizer.assigns_tenders and \
            not request.user.is_superuser and \
            not request.user.profile.is_planner(event.organizer) and \
            request.user in event.get_assigned_bartenders():
        raise PermissionDenied

    if request.method == 'POST' and request.is_ajax():
        bartender_availability, is_new_record = \
            BartenderAvailability.objects.get_or_create(
                user=request.user, event=event,
                defaults={'availability': availability})
        if not is_new_record:
            old_availability = bartender_availability.availability
            bartender_availability.availability = availability
            bartender_availability.save()
            log.availability_changed(
                request.user, event, request.user, old_availability,
                availability)
        else:
            log.availability_created(
                request.user, event, request.user, availability)
        return render(request, 'scheduling/partials/assigned_bartenders.html',
                      {'e': event})
    else:
        # TODO Better error message and HTTP status code [JZ]
        return HttpResponse("NOTOK")


def ical(request):
    events = Event.objects.filter(starts_at__gte=timezone.now() - timedelta(100)).order_by('starts_at')
    return IcalResponse(generate_ical(events))


def personal_ical(request, ical_id):
    profile = get_object_or_404(Profile, ical_id=ical_id)
    bas = profile.user.bartender_availability_set.filter(
        availability__nature=Availability.ASSIGNED,
        event__starts_at__gte=timezone.now() - timedelta(100)
    ). order_by('event__starts_at')
    events = []
    for ba in bas:
        events.append(ba.event)
    return IcalResponse(generate_ical(events,
                                      name='Tappersrooster %s' % profile.user.get_full_name(), tender=True))


class MailTemplateListView(ManagerRequiredMixin, TemplateView):
    """
    List view to show all existing and possible mail templates for the current organization.
    """

    template_name = 'scheduling/mailtemplate_list.html'

    def get_context_data(self, **kwargs):
        context = super(MailTemplateListView, self).get_context_data(**kwargs)

        organization = self.request.organization

        # All possible mail template names
        names = [name for name, description in MailTemplate.NAME_CHOICES]

        # Load existing mail templates
        mailtemplates = dict((mt.name, mt) for mt in MailTemplate.objects.filter(organization=organization))

        # Add dummy mail templates for non-existing templates
        for name in names:
            if name not in mailtemplates:
                mailtemplates[name] = MailTemplate(organization=organization, name=name)

        context['object_list'] = mailtemplates.values()

        return context


class MailTemplateObjectMixin(SingleObjectMixin):
    """
    Mixin to get a mail template based on given name or create a new object for the current organization
    with the given name.
    """

    def get_object(self, queryset=None):
        # Use a custom queryset if provided
        if queryset is None:
            queryset = self.get_queryset()

        # Get name from url
        name = self.kwargs['name']

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get(name=self.kwargs['name'])
        except queryset.model.DoesNotExist:
            # Create a new mail template with given name and current organization
            obj = self.model(organization=self.request.organization, name=name)
        return obj

    model = MailTemplate


class MailTemplateDetailView(MailTemplateObjectMixin, ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    pass


class MailTemplateUpdateView(MailTemplateObjectMixin, ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin,
                             UpdateView):
    model = MailTemplate
    fields = ['subject', 'template', 'is_active']


class AvailabilityListView(ManagerRequiredMixin, OrganizationFilterMixin, ListView):
    model = Availability


class AvailabilityCreateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin,
                             CreateViewForOrganization):
    model = Availability
    fields = ['name', 'nature']


class AvailabilityUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin, UpdateView):
    model = Availability
    fields = ['name', 'nature']
