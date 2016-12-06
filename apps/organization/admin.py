from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from apps.billing.admin import AuthorizationInline, RfidCardInline
from apps.scheduling.admin import AvailabilityInline

from .models import (
    AuthenticationData, Certificate, Location, Membership, Organization,
    Profile,
)

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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [
        ProfileInline,
        AuthenticationDataInline,
        MembershipInline,
        CertificateInline,
        RfidCardInline,
        AuthorizationInline,
    ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public')
    inlines = [
        AvailabilityInline,
    ]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fields = ['name', 'color', 'is_public', 'prevent_conflicting_events']
    list_display = ('name', 'is_public', 'prevent_conflicting_events')
