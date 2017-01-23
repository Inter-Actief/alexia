from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _

from alexia.apps.billing.models import Authorization, RfidCard
from alexia.apps.scheduling.models import Availability

from .models import (
    AuthenticationData, Certificate, Location, Membership, Organization,
    Profile,
)

admin.site.unregister(Group)
admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ['is_iva', 'is_bhv', 'is_foundation_manager']


class AuthenticationDataInline(admin.StackedInline):
    model = AuthenticationData
    exclude = ['additional_data']
    extra = 0


class MembershipInline(admin.TabularInline):
    model = Membership
    exclude = ['comments']
    extra = 0


class CertificateInline(admin.StackedInline):
    model = Certificate
    fk_name = 'owner'


class RfidCardInline(admin.TabularInline):
    model = RfidCard
    extra = 0
    readonly_fields = ['registered_at']
    raw_id_fields = ['managed_by']


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0
    exclude = ['account']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    inlines = [
        ProfileInline,
        AuthenticationDataInline,
        MembershipInline,
        CertificateInline,
        RfidCardInline,
        AuthorizationInline,
    ]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fields = [('name', 'prevent_conflicting_events'), 'color']
    list_display = ['name', 'prevent_conflicting_events']


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    fields = [('name', 'assigns_tenders'), 'color']
    inlines = [AvailabilityInline]
    list_display = ['name']
