from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.billing.admin import TemporaryProductInline
from .models import Availability, Event, MailTemplate, StandardReservation


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'name', 'subject', 'is_active')
    list_display_links = ('name',)
    list_filter = ('organization', 'name', 'is_active')
    search_fields = ('name', 'subject', 'template')


@admin.register(StandardReservation)
class StandardReservationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('organization', 'location', ('start_day', 'start_time'), ('end_day', 'end_time')),
        }),
    )
    list_display = ('organization', 'start_day', 'start_time', 'location')
    list_filter = ('organization', 'start_day', 'location')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('organizer', 'name', ('starts_at', 'ends_at'), ('location', 'participants'), 'kegs',
                       'pricegroup'),
        }),
        (_('Flags'), {
            'fields': ('is_closed', 'option', 'is_risky'),
        }),
        (_('Comments'), {
            'classes': ('collapse',),
            'fields': ('description', 'tender_comments'),
        }),
    )
    date_hierarchy = 'starts_at'
    list_display = ('organizer', 'name', 'starts_at', 'ends_at')
    list_display_links = ('name',)
    list_filter = ('organizer', 'participants', 'location')
    search_fields = ('name', 'description')
    inlines = [
        TemporaryProductInline,
    ]
