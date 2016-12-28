from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import EventManager
from .tools import notify_tenders


@python_2_unicode_compatible
class MailTemplate(models.Model):
    ENROLL_OPEN = 'enrollopen'
    ENROLL_CLOSED = 'enrollclosed'
    REMINDER = 'reminder'
    NAME_CHOICES = (
        (ENROLL_OPEN, _('Enrollment open')),
        (ENROLL_CLOSED, _('Enrollment closed')),
        (REMINDER, _('Weekly reminder')),
    )

    organization = models.ForeignKey('organization.Organization', models.CASCADE, verbose_name=_('organization'))
    name = models.CharField(_('name'), max_length=32, choices=NAME_CHOICES)
    subject = models.CharField(_('subject'), max_length=255)
    template = models.TextField(_('template'))
    is_active = models.BooleanField(_('is active'), default=False)

    class Meta:
        unique_together = ('organization', 'name')
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')

    def __str__(self):
        return '%s, %s' % (self.organization, self.get_name_display())

    def get_absolute_url(self):
        return reverse('mailtemplate_detail', args=[self.name])


@python_2_unicode_compatible
class Event(models.Model):
    organizer = models.ForeignKey(
        'organization.Organization',
        related_name='events',
        verbose_name=_('organizer'),
    )
    participants = models.ManyToManyField(
        'organization.Organization',
        related_name='participates',
        verbose_name=_('participants'),
    )
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(_('description'), blank=True)
    starts_at = models.DateTimeField(_('starts at'), db_index=True)
    ends_at = models.DateTimeField(_('ends at'), db_index=True)
    location = models.ManyToManyField(
        'organization.Location',
        related_name='events',
        verbose_name=_('location'),
    )
    is_closed = models.BooleanField(
        verbose_name=_('tender enrollment closed'),
        default=False,
        help_text=_(
            'Designates if tenders can sign up for this event.'
        ),
    )
    bartenders = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='BartenderAvailability',
        blank=True,
        verbose_name=_('bartenders'),
    )
    pricegroup = models.ForeignKey(
        'billing.PriceGroup',
        related_name='events',
        verbose_name=_('pricegroup'),
    )
    kegs = models.PositiveSmallIntegerField(verbose_name=_("number of kegs"))
    option = models.BooleanField(
        verbose_name=_('option'),
        default=False,
        help_text=_(
            'Designates that this event is not definitive yet.'
        ),
    )
    tender_comments = models.TextField(_('tender comments'), blank=True)
    is_risky = models.BooleanField(
        verbose_name=_('risky'),
        default=False,
        help_text=_(
            'Designates that this event should be marked as risky.'
        ),
    )

    objects = EventManager()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=[self.pk])

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
                Q(user__profile__is_iva=True) | Q(user__certificate__approved_at__isnull=False)).exists()

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
    NATURE_CHOICES = (
        (ASSIGNED, _('Assigned')),
        (YES, _('Yes')),
        (MAYBE, _('Maybe')),
        (NO, _('No')),
    )

    organization = models.ForeignKey(
        'organization.Organization',
        models.CASCADE,
        related_name='availabilities',
        verbose_name=_('organization'),
    )
    name = models.CharField(_('name'), max_length=32)
    nature = models.CharField(_('nature'), max_length=1, choices=NATURE_CHOICES)

    class Meta:
        unique_together = ('organization', 'name')
        verbose_name = _('availability type')
        verbose_name_plural = _('availability types')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('availability_detail', args=[self.pk])

    def css_class(self):
        classes = {
            self.ASSIGNED: 'info',
            self.YES: 'success',
            self.MAYBE: 'warning',
            self.NO: 'danger',
        }
        return classes[self.nature]


class BartenderAvailability(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('bartender'),
        related_name='bartender_availability_set',
    )
    event = models.ForeignKey(Event, verbose_name=_('event'), related_name='bartender_availabilities')
    availability = models.ForeignKey(Availability, verbose_name=_('availability'))

    class Meta:
        verbose_name = _('bartender availability')
        verbose_name_plural = _('bartender availabilities')
        unique_together = ('user', 'event')
