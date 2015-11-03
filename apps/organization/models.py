import os
from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from apps.scheduling.models import Event, Availability, BartenderAvailability
from .managers import PublicOrganizationManager


class Location(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=32)
    is_public = models.BooleanField(verbose_name=_('is public'), default=False)
    prevent_conflicting_events = models.BooleanField(
        verbose_name=_('prevent conflicting events'), default=True)
    color = models.CharField(verbose_name=_('Color'), blank=True, max_length=6,
                             validators=[RegexValidator(regex=r'^[0-9a-zA-Z]{6}$',
                                                        message=_('Enter a valid hexadecimal color'))])

    class Meta:
        ordering = ['name']
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __unicode__(self):
        return self.name

    def upcoming_event(self, threshold=timedelta(hours=5)):
        # Is er nu een event?
        try:
            result = self.events.get(starts_at__lte=datetime.now(),
                                     ends_at__gte=datetime.now())
        except Event.DoesNotExist:
            result = None

        if result is None:
            result = self.events.filter(
                starts_at__gt=datetime.now(),
                starts_at__lte=datetime.now() + threshold)[:1].get()

        return result


class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'))
    radius_username = models.CharField(_('RADIUS username'), max_length=10,
                                       unique=True)
    is_iva = models.BooleanField(_('has IVA-certificate'), default=False)
    is_bhv = models.BooleanField(_('has BHV-certificate'), default=False)
    certificate = models.OneToOneField('Certificate', null=True,
                                       verbose_name=_('certificate'))
    current_organization = models.ForeignKey('Organization', null=True,
                                             verbose_name=_('current organization'))
    ical_id = models.CharField(_('iCal identifier'), max_length=32,
                               null=True)

    class Meta:
        ordering = ['user']
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __unicode__(self):
        return unicode(self.user)

    def next_tending(self):
        return BartenderAvailability.objects.filter(
            user=self.user,
            event__ends_at__gte=timezone.now(),
            availability__nature=Availability.ASSIGNED) \
            .order_by('event__starts_at')[0].event

    def ical_url(self):
        return reverse('ical', args=[self.ical_id])

    def is_foundation_manager(self):
        return self.user.groups.filter(name='Foundation managers').exists()

    def is_manager(self, organization=None):
        if not organization:
            return self.user.membership_set.filter(is_manager=True).exists()
        else:
            return self.user.membership_set.filter(organization=organization,
                                                   is_manager=True).exists()

    def is_planner(self, organization=None):
        if not organization:
            return self.user.membership_set.filter(is_planner=True).exists()
        else:
            return self.user.membership_set.filter(organization=organization,
                                                   is_planner=True).exists()

    def is_tender(self, organization=None):
        if not organization:
            return self.user.membership_set.filter(is_tender=True).exists()
        else:
            return self.user.membership_set.filter(organization=organization,
                                                   is_tender=True).exists()

    def is_membership_or_higher(self, organization=None):
        return self.is_membership(organization) or self.is_planner_or_higher(organization)

    def is_planner_or_higher(self, organization=None):
        return self.is_planner() or self.is_organization_manager_or_higher(organization)

    def is_organization_manager_or_higher(self, organization=None):
        return self.is_manager(organization) or self.is_foundation_manager()

    def can_add_memberships(self, organization=None):
        return self.is_manager_or_higher(organization)

    def can_edit_memberships(self, organization=None):
        return self.is_manager_or_higher(organization)

    def can_add_events(self, organization=None):
        return self.is_planner_or_higher(organization)

    def can_edit_events(self, organization=None):
        return self.is_planner_or_higher(organization)

    def can_view_pricegroups(self, organization=None):
        return self.can_add_events(organization) or self.can_edit_events(organization)

    def can_edit_membershipavailability(self, user=None, organization=None):
        if user != self.user:
            return self.is_planner_or_higher(organization)
        else:
            return self.is_membership_or_higher(organization)

    def has_iva(self):
        try:
            approval_date = self.certificate.approved_at
        except AttributeError:
            approval_date = None

        return self.is_iva or approval_date

    def tended_count(self):
        return BartenderAvailability.objects.filter(
            user=self.user,
            event__ends_at__lte=timezone.now(),
            availability__nature=Availability.ASSIGNED).count()


class Organization(models.Model):
    name = models.CharField(_('name'), max_length=32, unique=True)
    slug = models.SlugField(_('slug'), editable=False, unique=True)
    is_public = models.BooleanField(_('is public'), default=False)
    color = models.CharField(verbose_name=_('Color'), blank=True, max_length=6,
                             validators=[RegexValidator(regex=r'^[0-9a-zA-Z]{6}$',
                                                        message=_('Enter a valid hexadecimal color'))])
    assigns_tenders = models.BooleanField(_('assigns tenders'), default=False)
    members = models.ManyToManyField(
        User, through='Membership', verbose_name=_('users'))

    objects = models.Manager()
    public_objects = PublicOrganizationManager()

    class Meta:
        ordering = ['name']
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, **kwargs):
        self.slug = slugify(self.__unicode__())
        super(Organization, self).save()


class Membership(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    organization = models.ForeignKey(
        Organization, verbose_name=_('organization'))
    comments = models.TextField(_('comments'), blank=True)
    is_tender = models.BooleanField(_('may tend on events'), default=False)
    is_planner = models.BooleanField(_('may create and modify events'), default=False)
    is_manager = models.BooleanField(_('may create and modify users'), default=False)

    class Meta:
        ordering = ('user', 'organization')
        unique_together = ('user', 'organization')
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __unicode__(self):
        return _('%(user)s of %(organization)s') % {
            'user': self.user.get_full_name(),
            'organization': self.organization}

    def get_absolute_url(self):
        return reverse('apps.organization.views.membership_show',
                       args=[self.pk])

    def tended(self):
        return BartenderAvailability.objects.filter(
            user=self.user,
            event__ends_at__lte=timezone.now(),
            availability__nature=Availability.ASSIGNED). \
            order_by('-event__starts_at')


def get_certificate_path(instance, filename):
    path = "certificates"
    ext = os.path.splitext(filename)[1]
    filename = instance._radius if instance._radius else "user" + instance._id
    return os.path.join(path, filename + ext)


class Certificate(models.Model):
    file = models.FileField(_('certificate'), upload_to=get_certificate_path)
    uploaded_at = models.DateField(auto_now_add=True,
                                   verbose_name=_('uploaded at'))
    approved_by = models.ForeignKey(User, related_name='approved_certificates',
                                    null=True, verbose_name=_('approved by'))
    approved_at = models.DateField(_('approved at'), null=True)

    def get_absolute_url(self):
        return reverse('apps.organization.views.membership_iva',
                       args=[self.pk])

    def approve(self, approver):
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()

    approve.alters_data = True

    def decline(self):
        profile = self.profile
        profile.certificate = None
        profile.save()
        self.delete()

    decline.alters_data = True


@receiver(pre_delete, sender=Certificate)
def certificate_delete(sender, instance, **kwargs):
    instance.file.delete(False)
