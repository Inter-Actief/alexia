from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from apps.billing.admin import AuthorizationInline, RfidCardInline, \
    PriceGroupInline, ProductGroupInline
from apps.scheduling.admin import AvailabilityInline, \
    StandardReservationInline
from .models import Location, Profile, Organization, Membership, Certificate


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False
    fields = ('is_bhv', 'is_iva')


class UserAdmin(UserAdmin):
    inlines = (ProfileInline, MembershipInline, AuthorizationInline, RfidCardInline)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public')
    list_filter = ('is_public',)
    inlines = (AvailabilityInline, StandardReservationInline,
               PriceGroupInline, ProductGroupInline)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'prevent_conflicting_events')
    list_filter = ('is_public', 'prevent_conflicting_events')
    inlines = (StandardReservationInline,)


class CertificateAdmin(admin.ModelAdmin):
    list_display = ('profile', 'uploaded_at', 'approved_at')
    search_fields = ('profile__user__first_name', 'profile__user__last_name', 'profile__user__username',)


admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Certificate, CertificateAdmin)
