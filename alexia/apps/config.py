from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BillingConfig(AppConfig):
    name = 'alexia.apps.billing'
    verbose_name = _('Billing')


class ConsumptionConfig(AppConfig):
    name = 'alexia.apps.consumption'
    verbose_name = _('Consumption')


class GeneralConfig(AppConfig):
    name = 'alexia.apps.general'
    verbose_name = _('General')


class JulianaConfig(AppConfig):
    name = 'alexia.apps.juliana'
    verbose_name = _('Juliana')


class OrganizationConfig(AppConfig):
    name = 'alexia.apps.organization'
    verbose_name = _('Organization')


class ProfileConfig(AppConfig):
    name = 'alexia.apps.profile'
    verbose_name = _('Profile')


class SchedulingConfig(AppConfig):
    name = 'alexia.apps.scheduling'
    verbose_name = _('Scheduling')
