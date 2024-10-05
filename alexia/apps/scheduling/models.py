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

    organization = models.ForeignKey('organization.Organization', on_delete=models.CASCADE, verbose_name=_('organization'))
    name = models.CharField(_('name'), max_length=32, choices=NAME_CHOICES)
    subject = models.CharField(_('subject'), max_length=255)
    template = models.TextField(_('template'))
    is_active = models.BooleanField(_('is active'), default=False)

    class Meta:
        ordering = ['organization']
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
        on_delete=models.CASCADE,
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
        on_delete=models.PROTECT,
        null=True,
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

    class Meta:
        ordering = ['-starts_at']
        verbose_name = _('event')
        verbose_name_plural = _('events')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=[self.pk])

    @staticmethod
    def conflicting_events(start, end, location=None):
        # An event is in the given interval if the event's start or end date
        # is in the given interval, or when the start date is before the given
        # interval and the end date is after the given interval.
        #
        #        START  --------------------------------- END
        #                                       o----------------
        #    --------------o
        #    o--------------------------------------------------o
        occuring_at = Event.objects.filter(
            (Q(starts_at__gt=start) & Q(starts_at__lt=end)) |  # start < start_date < end
            (Q(ends_at__gt=start) & Q(ends_at__lte=end)) |     # start < end_date < end
            (Q(starts_at__lte=start) & Q(ends_at__gte=end))    # start <= start_date & end_date => end
        )

        if location:
            occuring_at = occuring_at.filter(location=location)

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
        if user.is_superuser or user.profile.is_foundation_manager:
            return True

        return user in self.get_assigned_bartenders()

    def meets_iva_requirement(self):
        yes = 0
        no = 0

        for ba in self.bartender_availabilities.filter(
                Q(availability__nature=Availability.ASSIGNED)):
            if (hasattr(ba.user, 'certificate') and ba.user.certificate.approved_at) \
                    or ba.user.profile.is_iva:
                yes = yes + 1
            else:
                no = no + 1

        if yes and not no:
            return "YES"
        elif yes and no:
            return "MAYBE"
        else:
            return "NO"

    def needs_iva(self):
        return self.kegs > 0

    def visitors(self):
        return self.orders.values('authorization').distinct().count()


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
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name=_('organization'),
    )
    name = models.CharField(_('name'), max_length=32)
    nature = models.CharField(_('nature'), max_length=1, choices=NATURE_CHOICES)
    position = models.IntegerField(_('position'), default=1)

    class Meta:
        unique_together = ('organization', 'name')
        verbose_name = _('availability type')
        verbose_name_plural = _('availability types')
        ordering = ['position']

    def __str__(self):
        return self.name

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
        on_delete=models.CASCADE,
        verbose_name=_('bartender'),
        related_name='bartender_availability_set',
    )
    event = models.ForeignKey(
        Event,
        verbose_name=_('event'),
        related_name='bartender_availabilities',
        on_delete=models.CASCADE,
    )
    availability = models.ForeignKey(
        Availability,
        verbose_name=_('availability'),
        on_delete=models.CASCADE,
    )
    comment = models.TextField(_('comment'), blank=True, default='', max_length=100)

    class Meta:
        verbose_name = _('bartender availability')
        verbose_name_plural = _('bartender availabilities')
        unique_together = ('user', 'event')
