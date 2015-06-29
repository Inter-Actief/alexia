from django.contrib import admin

from apps.billing.admin import TemporaryProductInline
from apps.stock.admin import EventConsumptionInline
from .models import StandardReservation, Event, \
    Availability, MailTemplate


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


class StandardReservationInline(admin.TabularInline):
    model = StandardReservation
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = (EventConsumptionInline, TemporaryProductInline)
    date_hierarchy = 'starts_at'
    list_display = ('organizer', 'name', 'starts_at', 'ends_at')
    list_display_links = ('name',)
    list_filter = ('organizer', 'participants', 'location')
    search_fields = ('name', 'description')


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'name', 'subject', 'is_active')
    list_display_links = ('organization', 'name')
    list_filter = ('organization', 'is_active')
    search_fields = ('name', 'subject', 'template')


class StandardReservationAdmin(admin.ModelAdmin):
    list_display = ('organization', 'start_day', 'start_time', 'location')
    list_filter = ('organization', 'start_day', 'location')


admin.site.register(Event, EventAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)
admin.site.register(StandardReservation, StandardReservationAdmin)
