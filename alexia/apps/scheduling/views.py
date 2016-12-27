import collections
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.query import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from alexia.apps.organization.forms import BartenderAvailabilityForm
from alexia.apps.organization.models import Membership, Profile
from alexia.apps.scheduling.forms import EventForm, FilterEventForm
from alexia.apps.scheduling.models import (
    Availability, BartenderAvailability, Event, MailTemplate,
)
from alexia.auth.decorators import planner_required
from alexia.auth.mixins import ManagerRequiredMixin
from alexia.forms import CrispyFormMixin
from alexia.http import IcalResponse
from alexia.utils import log
from alexia.utils.calendar import generate_ical
from alexia.utils.mixins import (
    CreateViewForOrganization, OrganizationFilterMixin,
)


# =========================================================================
# PAGES
# =========================================================================


def overview(request):
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

    # Rechten opslaan
    is_planner = request.user.is_authenticated() and (
        request.user.is_superuser or (request.organization and request.user.profile.is_planner(request.organization)))
    is_tender = request.user.is_authenticated() and request.organization and request.user.profile.is_tender(
        request.organization)

    # Gebruiker opslaan
    user = request.user

    return render(request, 'scheduling/overview_list.html', locals())


# =========================================================================
# Events
# =========================================================================
def event_show(request, pk):
    event = get_object_or_404(Event, pk=pk)

    is_tender = event.is_tender(request.user)
    is_planner = request.user.is_authenticated() and request.user.profile.is_planner(event.organizer)
    is_manager = request.user.is_authenticated() and request.user.profile.is_manager(event.organizer)

    if is_planner:
        tenders = Membership.objects.select_related('user').filter(
            organization__in=event.participants.all(), is_tender=True). \
            order_by("is_active", "user__first_name")
        bas = collections.defaultdict(list)

        for ba in BartenderAvailability.objects.select_related().filter(event=event):
            bas[ba.user].append(ba)

        active_availabilities = []
        inactive_availabilities = []
        for t in tenders:
            ba = bas[t.user]
            a = ba[0].availability if ba else None
            t_info = {'user': t.user,
                      'availability': a,
                      'membership_id': t.pk,
                      'last_tended': t.tended()[0] if len(t.tended()) > 0 else None
                      }
            if t.is_active:
                active_availabilities.append(t_info)
            else:
                inactive_availabilities.append(t_info)

    return render(request, 'scheduling/event_show.html', locals())


@login_required
@planner_required
def event_add(request):
    if not request.organization:
        raise PermissionDenied(_('Creating an event requires an primary organization.'))

    if request.method == 'POST':
        form = EventForm(request, request.POST)
        if form.is_valid():
            event = form.save(commit=False, organizer=request.organization)
            event.organizer = request.organization
            event.save()
            form.save_m2m()
            log.event_created(request.user, event)
            return redirect(overview)
    else:
        form = EventForm(request)

    return render(request, 'scheduling/event_form.html', locals())


@login_required
@planner_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.organization:
        raise PermissionDenied

    if request.method == 'POST':
        form = EventForm(request, request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            log.event_modified(request.user, event)
            return redirect(overview)
    else:
        form = EventForm(instance=event)

    return render(request, 'scheduling/event_form.html', locals())


@login_required
@planner_required
def event_edit_bartender_availability(request, pk, user_pk):
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
            return redirect(event_show, pk=event.pk)
    else:
        form = BartenderAvailabilityForm(instance=bartender_availability,
                                         event=event, user=user)

    return render(request, 'scheduling/event_bartender_availability_form.html', locals())


@login_required
@planner_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.organization:
        raise PermissionDenied

    if request.method == 'POST':
        event.delete()
        log.event_deleted(request.user, event)
        return redirect(overview)
    else:
        return render(request, 'scheduling/event_delete.html', locals())


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


class AvailabilityDetailView(ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    model = Availability


class AvailabilityCreateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin,
                             CreateViewForOrganization):
    model = Availability
    fields = ['name', 'nature']


class AvailabilityUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin, UpdateView):
    model = Availability
    fields = ['name', 'nature']
