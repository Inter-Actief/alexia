from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from alexia.apps.billing.models import TemporaryProduct

from .models import Event, MailTemplate


class TemporaryProductInline(admin.TabularInline):
    model = TemporaryProduct


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'starts_at'
    fieldsets = (
        (None, {
            'fields': ('organizer', 'name', ('starts_at', 'ends_at'), ('location', 'participants'), 'kegs',
                       'pricegroup'),
        }),
        (_('Flags'), {'fields': ('is_closed', 'option', 'is_risky')}),
        (_('Comments'), {'fields': (('description', 'tender_comments'),)}),
    )
    inlines = [TemporaryProductInline]
    list_display = ['organizer', 'name', 'starts_at', 'ends_at']
    list_display_links = ['name']
    list_filter = ['organizer', 'participants', 'location']
    search_fields = ['name', 'description']


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['organization', 'name', 'subject', 'is_active']
    list_display_links = ['name']
    list_filter = ['organization', 'name', 'is_active']
    search_fields = ['name', 'subject', 'template']
