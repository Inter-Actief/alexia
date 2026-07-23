import os
from typing import Optional

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from alexia.apps.organization import managers
from alexia.apps.scheduling.models import Availability, BartenderAvailability
from alexia.core.validators import validate_color


class Location(models.Model):
    name = models.CharField(_('name'), max_length=32)
    prevent_conflicting_events = models.BooleanField(_('prevent conflicting events'), default=True)
    color = models.CharField(_('color'), blank=True, max_length=6, validators=[validate_color])

    class Meta:
        ordering = ['name']
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __str__(self):
        return self.name


class AuthenticationData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    backend = models.CharField(_('authentication backend'), max_length=50)
    username = models.CharField(_('username'), max_length=50)
    additional_data = models.TextField(_('additional data'), null=True)

    class Meta:
        unique_together = (('backend', 'username'), ('user', 'backend'))


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        unique=True,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    is_iva = models.BooleanField(
        _('has IVA-certificate'),
        default=False,
        help_text=_(
            'Override for an user to indicate IVA rights without uploading a certificate.'
        ),
    )
    is_bhv = models.BooleanField(
        _('has BHV-certificate'),
        default=False,
        help_text=_(
            'Designates that this user has a valid, non-expired BHV (Emergency Response Officer) certificate.'
        ),
    )
    is_foundation_manager = models.BooleanField(
        _('is foundation manager'),
        default=False,
        help_text=_(
            'Designates that this user is manager of the purchasing foundation.'
        ),
    )
    current_organization = models.ForeignKey(
        'Organization',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('current organization'),
    )
    ical_id = models.CharField(_('iCal identifier'), max_length=36, null=True)
    nickname = models.CharField(_('bartender nickname'), max_length=32, blank=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return str(self.user)

    def is_manager(self, organization):
        if self.user.is_superuser:
            return True
        return self.user.membership_set.filter(organization=organization, is_manager=True).exists()

    def is_planner(self, organization):
        if self.user.is_superuser:
            return True
        return self.user.membership_set.filter(organization=organization, is_planner=True).exists()

    def is_tender(self, organization):
        if self.user.is_superuser:
            return True
        return self.user.membership_set.filter(organization=organization, is_tender=True).exists()

    def has_iva(self):
        try:
            approval_date = self.user.certificate.approved_at
        except AttributeError:
            approval_date = None

        return self.is_iva or approval_date

    def tended_count(self):
        return BartenderAvailability.objects.filter(
            Q(event__kegs__gt=0) | Q(event__consumptionform__isnull=False) | Q(event__orders=True) |
                Q(event__ends_at__lte=timezone.datetime(2016, 12, 13)),  # Date of first consumption form
            user=self.user,
            event__ends_at__lte=timezone.now(),
            availability__nature=Availability.ASSIGNED,
        ).distinct().count()

    def get_bartender_name(self):
        return (self.nickname or self.user.first_name)


class Organization(models.Model):
    name = models.CharField(_('name'), max_length=32, unique=True)
    slug = models.SlugField(_('slug'), editable=False, unique=True)
    color = models.CharField(verbose_name=_('color'), blank=True, max_length=6, validators=[validate_color])
    assigns_tenders = models.BooleanField(_('assigns tenders'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    writeoff_enabled = models.BooleanField(_('writeoff enabled'), default=False)
    age_check_enabled = models.BooleanField(_('age check enabled'), default=False)
    age_check_api_endpoint = models.URLField(_('age check API endpoint'), blank=True, null=True)
    age_check_api_key = models.CharField(_('age check API key'), max_length=64, blank=True, null=True)
    card_registration_url = models.URLField(_('card registration URL'), blank=True, null=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Membership',
        verbose_name=_('users'),
    )

    objects = managers.ActiveOrganizationManager()

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')

    def __str__(self):
        return self.name

    def clean(self):
        if self.age_check_enabled and (not self.age_check_api_endpoint or not self.age_check_api_key):
            raise ValidationError(
                _('You must specify an API endpoint and an API key if you enable the age check functionality.')
            )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.__str__())
        super(Organization, self).save(*args, **kwargs)

    def age_check_rfid(self, rfid_code: str) -> Optional[bool]:
        """
        If the organization has age checking enabled, send a check request to their API endpoint
        to see if the RFID code passes the age check.

        If the feature is not enabled, always returns True as if the check was successful.

        :param rfid_code: The RFID code to check.
        :return: The age check result.
        """
        if self.age_check_enabled:
            try:
                res = requests.post(
                    self.age_check_api_endpoint,
                    json={'apiKey': self.age_check_api_key, 'rfid': rfid_code}
                )
                if res.status_code == 200:
                    result = res.json()
                    if 'check_ok' in result and isinstance(result['check_ok'], bool):
                        return result['check_ok']
            except requests.exceptions.RequestException:
                pass
            return None
        else:
            # If age checking is not enabled, always returns True as if the check was successful.
            return True


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_('organization')
    )
    comments = models.TextField(_('comments'), blank=True)
    is_tender = models.BooleanField(_('may tend on events'), default=False)
    is_planner = models.BooleanField(_('may create and modify events'), default=False)
    is_manager = models.BooleanField(_('may create and modify users'), default=False)
    is_active = models.BooleanField(_('is currently active'), default=True)

    class Meta:
        unique_together = ('user', 'organization')
        verbose_name = _('membership')
        verbose_name_plural = _('memberships')

    def __str__(self):
        return _('%(user)s of %(organization)s') % {
            'user': self.user.get_full_name(),
            'organization': self.organization,
        }

    def get_absolute_url(self):
        return reverse('membership', args=[self.pk])

    def tended(self):
        return BartenderAvailability.objects.select_related('event').filter(
            user=self.user,
            event__ends_at__lte=timezone.now(),
            availability__nature=Availability.ASSIGNED
        ).order_by('-event__starts_at')

    def last_tended(self):
        event = self.user.bartender_availability_set.select_related('event').filter(
            event__ends_at__lte=timezone.now(),
            availability__nature=Availability.ASSIGNED
        ).order_by('-event__starts_at')

        if not event:
            return None
        else:
            event = event[0].event
            return '%s - %s ' % (
                event.starts_at.strftime('%d-%m-%Y'),
                event.name,
            )


def _get_certificate_path(instance, filename):
    path = "certificates"
    ext = os.path.splitext(filename)[1]
    filename = "user" + str(instance.owner_id)
    return os.path.join(path, filename + ext)


class Certificate(models.Model):
    file = models.FileField(_('certificate'), upload_to=_get_certificate_path)
    uploaded_at = models.DateField(auto_now_add=True, verbose_name=_('uploaded at'))
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approved_certificates',
        null=True,
        verbose_name=_('approved by'),
    )
    approved_at = models.DateField(_('approved at'), null=True)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('certificate'),
    )

    def __str__(self):
        return '%s %s' % (
            _('IVA certificate of'),
            self.owner.get_full_name(),
        )

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(Certificate, self).delete(*args, **kwargs)

    delete.alters_data = True

    def approve(self, approver):
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()

    approve.alters_data = True

    def decline(self):
        self.delete()

    decline.alters_data = True
