# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import EventConsumption, StockProduct, Consumption, \
    StockCount, StockProductAmount


class EventConsumptionInline(admin.TabularInline):
    model = EventConsumption
    extra = 0


class StockProductAmountInline(admin.TabularInline):
    model = StockProductAmount
    extra = 3


class ConsumptionInline(admin.TabularInline):
    model = Consumption
    extra = 3
    raw_id_fields = ('group',)


class StockProductAdmin(admin.ModelAdmin):
    pass


class EventConsumptionAdmin(admin.ModelAdmin):
    inlines = (ConsumptionInline,)
    date_hierarchy = 'opened_at'
    list_display = ('event', 'opened_at', 'closed_at')
    list_filter = ('event__organizer',)
    raw_id_fields = ('event',)


class StockCountAdmin(admin.ModelAdmin):
    inlines = (StockProductAmountInline,)
    exclude = ('products',)
    date_hierarchy = 'date'
    list_display = ('date', 'organization', 'is_completed')
    list_filter = ('organization',)
    raw_id_fields = ('user',)


admin.site.register(StockProduct, StockProductAdmin)
admin.site.register(EventConsumption, EventConsumptionAdmin)
admin.site.register(StockCount, StockCountAdmin)
