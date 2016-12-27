from __future__ import unicode_literals

import math
from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import EventManager
from .tools import notify_tenders


@python_2_unicode_compatible
class MailTemplate(models.Model):
    NAME_CHOICES = (
        ('enrollopen', _('Enrollment open')),
        ('enrollclosed', _('Enrollment closed')),
        ('reminder', _('Weekly reminder')),
    )

    organization = models.ForeignKey('organization.Organization', models.CASCADE, verbose_name=_('organization'))
    name = models.CharField(_('name'), max_length=32, choices=NAME_CHOICES)
    subject = models.CharField(_('subject'), max_length=255)
    template = models.TextField(_('template'))
    is_active = models.BooleanField(_('is active'), default=False)

    class Meta:
        ordering = ['organization', 'name']
        unique_together = ('organization', 'name')
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')

    def __str__(self):
        return '%s, %s' % (self.organization, self.get_name_display())

    def get_absolute_url(self):
        return reverse('mailtemplate_detail', args=[self.name])


@python_2_unicode_compatible
class Event(models.Model):
    organizer = models.ForeignKey('organization.Organization', related_name='events', verbose_name=_("organizer"))
    participants = models.ManyToManyField(
        'organization.Organization',
        related_name='participates',
        verbose_name=_("participants"),
    )
    name = models.CharField(_("name"), max_length=128)
    description = models.TextField(_("description"), blank=True)
    starts_at = models.DateTimeField(_("starts at"), db_index=True)
    ends_at = models.DateTimeField(_("ends at"), db_index=True)
    location = models.ManyToManyField('organization.Location', related_name='events', verbose_name=_("location"))
    is_closed = models.BooleanField(
        verbose_name=_("tender enrollment closed"),
        default=False,
        help_text=_(
            'Designates if tenders can sign up for this event.'
        ),
    )
    bartenders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='BartenderAvailability',
        blank=True,
        verbose_name=_("bartenders"),
    )
    pricegroup = models.ForeignKey('billing.PriceGroup', related_name='events', verbose_name=_("pricegroup"))
    kegs = models.PositiveSmallIntegerField(verbose_name=_("number of kegs"))
    option = models.BooleanField(
        verbose_name=_("option"),
        default=False,
        help_text=_(
            'Designates that this event is not definitive yet.'
        ),
    )
    tender_comments = models.TextField(_("tender comments"), blank=True)
    is_risky = models.BooleanField(
        verbose_name=_("risky"),
        default=False,
        help_text=_(
            'Designates that this event should be marked as risky.'
        ),
    )

    objects = EventManager()

    class Meta:
        ordering = ['-starts_at']
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=[self.pk])

    def must_ducts_be_flushed(self, location=None):
        """Returns true if this is the last drink of the week or there hasn't
        been a drink in two weeks in this location.
        """
        # If no location specified, use all locations for the current event.
        # This is recursive.
        if not location:
            for l in self.location.all():
                if self.must_ducts_be_flushed(l):
                    return True

        else:
            # Check for two weeks ago
            two_weeks_ago = self.starts_at - timedelta(weeks=2)
            if not Event.objects.occuring_at(two_weeks_ago, self.starts_at). \
                    filter(location=location).exists():
                return True

            # Check for last event in the week
            days_until_sunday = sunday = 7 - self.ends_at.isoweekday()
            sunday = (self.ends_at + timedelta(days=days_until_sunday)). \
                replace(hour=23, minute=59, second=59, microsecond=0)
            if not Event.objects.occuring_at(self.ends_at, sunday). \
                    filter(location=location).exists():
                return True

        # No case matched
        return False

    @staticmethod
    def conflicting_events(start, end, location=None):
        """Returns a list of all events that conflict. If a location is given,
        the events within the time range at that location is returned. If no
        location is given, all public locations are assumed.
        """

        occuring_at = Event.objects.occuring_at(start, end)
        if location:
            occuring_at = occuring_at.filter(location=location)
        else:
            occuring_at = occuring_at.filter(location__is_public=True)

        return occuring_at

    def is_at_time(self, t):
        """Returns whether this event is at the given time, but not if it
        starts or ends at the given time.
        """

        if (self.ends_at - self.starts_at) >= timedelta(days=1):
            return True

        st = self.starts_at.time()
        sd = self.starts_at.date()
        et = self.ends_at.time()
        ed = self.ends_at.date()

        if sd == ed:
            return st < t < et
        else:
            return st < t or t < et

        return (st < et and st < t < et) or (st > et and et < t < st)

    def time_until(self, t):
        """Returns a timedelta object until the next occurence of t,
        relative to the start date of the event."""

        if self.starts_at.time() < t:
            next_t = datetime.combine(self.starts_at.date(), t)
        else:
            next_t = datetime.combine(
                self.starts_at.date() + timedelta(days=1), t)

        if settings.USE_TZ:
            next_t = timezone.make_aware(
                next_t, timezone.get_default_timezone())
        return next_t - self.starts_at

    def get_rounded_starts_at(self):
        """Rounds the event's start date to full quarters."""
        return (self.starts_at - timedelta(minutes=self.starts_at.minute % 15)).replace(second=0)

    def get_hour_rounded_starts_at(self):
        """Rounds the event's start date to full hours."""
        return (self.starts_at -
                timedelta(minutes=self.starts_at.minute)).replace(second=0)

    def get_rounded_ends_at(self):
        """Rounds the event's end date to full quarters."""
        return (self.ends_at + timedelta(minutes=15 - (self.ends_at.minute % 15))).replace(second=0)

    def get_hour_rounded_ends_at(self):
        """Rounds the event's end date to full hours."""
        return (self.ends_at + timedelta(minutes=60 - self.ends_at.minute)).replace(second=0)

    def get_duration_minutes(self):
        """Returns the duration in minutes for this event.
        """
        start = self.starts_at.replace(second=0)
        end = self.ends_at

        if self.ends_at.second != 0:
            end += timedelta(seconds=60 - self.ends_at.second)
        duration = (end - start).seconds + (end - start).days * 60 * 60 * 24
        minutes = int(math.ceil(duration / 60))
        return minutes

    def get_rounded_duration_quarters(self):
        """Returns the duration in quarters for this event. It uses the rounded
        event dates.
        """
        start = self.get_rounded_starts_at()
        end = self.get_rounded_ends_at()
        duration = (end - start).seconds + (end - start).days * 60 * 60 * 24
        quarters = int(math.ceil(duration / 900))
        return quarters

    def get_quarters_without_conflict(self, location=None):
        """Returns all quarters that don't have a conflict with another
        existing event. If a location is given, only events at that location
        are checked. If no location is given, all public locations are assumed.
        The returned list contains all quarters, starting at 0, relatively
        numbered to the start of the event, at which no conflicts were found.
        """
        quarters = self.get_duration_quarters()
        valid_quarters = []

        for q in range(quarters):
            quarter_start = self.get_rounded_starts_at() + timedelta(
                minutes=15 * q)
            quarter_end = self.get_rounded_starts_at() + timedelta(
                minutes=15 * (q + 1))

            conflicts = Event.conflicting_events(
                quarter_start, quarter_end, location)

            if (self in conflicts and len(conflicts) == 1) or len(conflicts) == 0:
                valid_quarters.append(q)

        return valid_quarters

    def get_non_conflicting_quarters_after_event(self, location=None):
        """Gets the range of free quarters between the next event at
        the given location (or, if None given, all public locations)
        and the current event. If no next event is found, or the
        location is not free at the end of this event, 0 is returned.
        """
        next_event = Event.objects.filter(
            ends_at__gt=self.ends_at).order('starts_at')
        if location:
            next_event = next_event.filter(location=location)
        else:
            next_event = next_event.filter(location__is_public=True)

        if not next_event:  # No events found
            return []
        # The next event is not ended yet
        elif next_event.get_rounded_starts_at() <= self.get_rounded_ends_at():
            return []
        # WE must calculate the difference between the current end date
        # and the new start date in quarters
        else:
            return range(math.ceil((next_event.get_rounded_starts_at() -
                                    self.get_rounded_ends_at()).seconds / 900))

    def event_number_of_quarters(self):
        return (self.starts_at - self.ends_at).seconds / 900

    def copy(self):
        initial = dict([(f.name, getattr(self, f.name))
                        for f in self._meta.fields
                        if f not in self._meta.parents.values()])
        return self.__class__(**initial)

    def get_assigned_bartenders(self):
        # Result could be cached by earlier call or prefetch
        if not hasattr(self, 'bartender_availabilities_assigned'):
            self.bartender_availabilities_assigned = self.bartender_availabilities.filter(
                availability__nature=Availability.ASSIGNED)
        return [x.user for x in self.bartender_availabilities_assigned]

    def can_be_opened(self, user=None):
        if user and user.is_superuser:
            return True

        return (self.starts_at - timedelta(hours=5)) <= timezone.now() <= \
               (self.ends_at + timedelta(hours=24))

    def is_tender(self, user):
        """
        Returns if the given person is a tender for this event.
        """
        if user.is_superuser:
            return True

        return user in self.get_assigned_bartenders()

    def meets_iva_requirement(self):
        # Result could be cached by earlier call or prefetch
        if not hasattr(self, 'bartender_availabilities_iva'):
            self.bartender_availabilities_iva = self.bartender_availabilities.filter(
                Q(availability__nature=Availability.ASSIGNED),
                Q(user__profile__is_iva=True) | Q(user__profile__certificate__approved_at__isnull=False)).exists()

        return bool(self.bartender_availabilities_iva)

    def needs_iva(self):
        return self.kegs > 0


pre_save.connect(notify_tenders, Event)


@python_2_unicode_compatible
class Availability(models.Model):
    ASSIGNED = 'A'
    YES = 'Y'
    MAYBE = 'M'
    NO = 'N'
    NATURES = ((ASSIGNED, _("Assigned")), (YES, _("Yes")), (MAYBE, _("Maybe")), (NO, _("No")))

    organization = models.ForeignKey(
        'organization.Organization',
        related_name='availabilities',
        verbose_name=_("organization"),
    )
    name = models.CharField(_("name"), max_length=32)
    nature = models.CharField(_("nature"), max_length=1, choices=NATURES)

    class Meta:
        ordering = ['organization', 'name']
        unique_together = ('organization', 'name')
        verbose_name = _("availability type")
        verbose_name_plural = _("availability types")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('availability_detail', args=[self.pk])

    def is_assigned(self):
        return self.nature == Availability.ASSIGNED

    def is_yes(self):
        return self.nature == Availability.YES

    def is_maybe(self):
        return self.nature == Availability.MAYBE

    def is_no(self):
        return self.nature == Availability.NO

    def css_class(self):
        if self.is_assigned():
            return 'info'
        if self.is_yes():
            return 'success'
        if self.is_maybe():
            return 'warning'
        if self.is_no():
            return 'danger'


class BartenderAvailability(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("bartender"),
        related_name='bartender_availability_set',
    )
    event = models.ForeignKey(Event, verbose_name=_("event"), related_name='bartender_availabilities')
    availability = models.ForeignKey(Availability, verbose_name=_("availability"))

    class Meta:
        verbose_name = _("bartender availability")
        verbose_name_plural = _("bartender availabilities")
        unique_together = ('user', 'event')
