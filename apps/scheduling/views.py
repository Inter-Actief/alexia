from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.query import Prefetch
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, \
    redirect
from django.utils import timezone

from apps.organization.forms import BartenderAvailabilityForm
from apps.scheduling.forms import EventForm, EditEventForm, \
    MailTemplateForm, StandardReservationForm, FilterEventForm
from apps.scheduling.models import Event, BartenderAvailability, \
    Availability, MailTemplate, StandardReservation
from apps.organization.models import Membership, \
    Profile
from utils import log
from utils.calendar import generate_ical, IcalResponse
from utils.auth.decorators import planner_required


# =========================================================================
# PAGES
# =========================================================================


def overview(request):
    # De lijst waarop we nog gaan filteren
    events = Event.objects.select_related().prefetch_related(
        'participants', 'location').order_by('starts_at')
    events = events.prefetch_related(Prefetch('bartender_availabilities',
                                              queryset=BartenderAvailability.objects.filter(
                                                  availability__nature=Availability.YES),
                                              to_attr='bartender_availabilities_yes'),
                                     'bartender_availabilities_yes__user',
                                     Prefetch('bartender_availabilities',
                                              queryset=BartenderAvailability.objects.filter(
                                                  Q(availability__nature=Availability.YES),
                                                  Q(user__profile__is_iva=True) |
                                                  Q(user__profile__certificate__approved_at__isnull=False)),
                                              to_attr='bartender_availabilities_iva'),
                                     )

    # Default from_time is now.
    from_time = timezone.now()

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
                events = events.filter(starts_at__lte=data['till_time'])

    else:
        filter_form = FilterEventForm()

    events = events.filter(ends_at__gte=from_time)

    # Dubbele resultaten weghalen
    events = events.distinct()

    if request.user.is_authenticated():
        events_tending = events.filter(bartender_availabilities__availability__nature=Availability.YES,
                                       bartender_availabilities__user=request.user) \
            .select_related(None).prefetch_related(None).order_by()

    # Beschikbaarheden in een lijstje stoppen
    availabilities = list(request.organization.availabilities.all()) \
        if request.organization else []
    # Net als onze BartenderAvailabilities
    bartender_availabilities = BartenderAvailability.objects.filter(
        user_id=request.user.pk).values('event_id', 'availability_id')

    # Rechten opslaan
    is_planner = request.user.is_superuser or (
        request.organization and
        request.user.profile.is_planner(request.organization))
    is_tender = request.organization and request.user.profile.is_tender(
        request.organization)

    return render(request, 'scheduling/overview_list.html', locals())


# =========================================================================
# Events
# =========================================================================
@login_required
@planner_required
def event_show(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.organization:
        raise PermissionDenied

    tenders = Membership.objects.filter(
        organization__in=event.participants.all(), is_tender=True). \
        order_by("user__first_name")

    availability = BartenderAvailability.objects.filter(event=event)
    available_yes = availability.filter(
        availability__nature=Availability.YES). \
        values_list('user_id', flat=True)
    available_maybe = availability.filter(
        availability__nature=Availability.MAYBE). \
        values_list('user_id', flat=True)
    available_no = availability.filter(
        availability__nature=Availability.NO).values_list('user_id', flat=True)

    is_manager = request.user.profile.is_manager(request.organization)

    return render(request, 'scheduling/event_show.html', locals())


@login_required
@planner_required
def event_add(request):
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
        form = EditEventForm(request, request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            log.event_modified(request.user, event)
            return redirect(overview)
    else:
        form = EditEventForm(instance=event)

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
        return render(request, 'scheduling/partials/available_bartenders.html',
                      {'e': event})
    else:
        # TODO Better error message and HTTP status code [JZ]
        return HttpResponse("NOTOK")


# =========================================================================
# Templates
# =========================================================================


def edit_mailtemplates(request):
    organization = request.organization
    if request.method == "POST":
        form = MailTemplateForm(data=request.POST)
        if form.is_valid():
            mt = MailTemplate.objects.get(pk=form.cleaned_data['template_id'])
            form = MailTemplateForm(instance=mt, data=request.POST)
            mt = form.save(commit=False)
            mt.organization = organization
            mt.save()
            return render(request, 'closepopup.html', {})

    else:
        resobject = MailTemplate.objects.get(
            organization=organization, name='reservations')
        enrobject = MailTemplate.objects.get(
            organization=organization, name='enrollopen')
        remobject = MailTemplate.objects.get(
            organization=organization, name='reminder')
        fusobject = MailTemplate.objects.get(
            organization=organization, name='fustdiff')

        reservations = MailTemplateForm(instance=resobject, template=resobject)
        enrollopen = MailTemplateForm(instance=enrobject, template=enrobject)
        reminder = MailTemplateForm(instance=remobject, template=remobject)
        fustdiff = MailTemplateForm(instance=fusobject, template=fusobject)

    return render(request, 'scheduling/mailtemplates.html',
                  {'reservations': reservations, 'enrollopen': enrollopen,
                   'reminder': reminder, 'fustdiff': fustdiff})


def edit_standardreservations(request):
    StandardReservationFormset = modelformset_factory(
        StandardReservation, form=StandardReservationForm, can_delete=True)
    if request.method == "POST":
        formset = StandardReservationFormset(request.POST)
        if formset.is_valid():
            formset.save()

            return render(request, 'closepopup.html', {})
    else:
        formset = StandardReservationFormset(
            queryset=StandardReservation.objects.all())
    return render(request, 'scheduling/standardreservations.html',
                  {'formset': formset})


def ical(request):
    events = Event.objects.filter(starts_at__gte=timezone.now() - timedelta(100)).order_by('starts_at')
    return IcalResponse(generate_ical(events))


def personal_ical(request, ical_id):
    profile = get_object_or_404(Profile, ical_id=ical_id)
    bas = profile.user.bartender_availability_set.filter(
        availability__nature=Availability.YES,
        event__starts_at__gte=timezone.now() - timedelta(100)
    ). order_by('event__starts_at')
    events = []
    for ba in bas:
        events.append(ba.event)
    return IcalResponse(generate_ical(events,
                                      name='Tappersrooster %s' % profile.user.get_full_name(), tender=True))
