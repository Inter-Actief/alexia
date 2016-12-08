from django.contrib import admin

from .models import (
    ConsumptionForm, ConsumptionProduct, UnitEntry, WeightConsumptionProduct,
    WeightEntry,
)


class WeightConsumptionProductInline(admin.StackedInline):
    model = WeightConsumptionProduct
    extra = 0


class UnitEntryInline(admin.TabularInline):
    model = UnitEntry


class WeightEntryInline(admin.TabularInline):
    model = WeightEntry


@admin.register(ConsumptionProduct)
class ConsumptionProductAdmin(admin.ModelAdmin):
    inlines = [
        WeightConsumptionProductInline,
    ]


@admin.register(ConsumptionForm)
class ConsumptionFormAdmin(admin.ModelAdmin):
    date_hierarchy = 'completed_at'
    list_display = ('__str__', 'completed_at')
    raw_id_fields = ('event', 'completed_by')
    inlines = [
        UnitEntryInline,
        WeightEntryInline,
    ]
