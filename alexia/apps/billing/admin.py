from django.contrib import admin

from .models import (
    Authorization, Order, PermanentProduct, PriceGroup, ProductGroup, Purchase,
    RfidCard, SellingPrice, WriteOffOrder,
)


@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    fields = ['user', 'organization', ('start_date', 'end_date')]
    list_display = ['user', 'owner', 'organization', 'start_date', 'end_date']
    list_filter = ['organization', 'start_date', 'end_date']
    raw_id_fields = ['user']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']


class PurchaseInline(admin.TabularInline):
    model = Purchase
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.synchronized:
            return self.readonly_fields + ('product', 'amount', 'price')
        return self.readonly_fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'placed_at'
    fields = ['event', 'authorization', 'placed_at', 'rfidcard', 'added_by', 'synchronized']
    inlines = [PurchaseInline]
    list_display = ['event', 'debtor', 'placed_at', 'amount', 'synchronized']
    list_filter = ['authorization__organization', 'placed_at']
    raw_id_fields = ['added_by', 'authorization', 'event', 'rfidcard']
    readonly_fields = ['placed_at', 'synchronized']
    search_fields = ['authorization__user__first_name', 'authorization__user__last_name',
                     'authorization__user__username']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.synchronized:
            return self.readonly_fields + self.fields
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        formset.save()
        form.instance.save()  # Updates Order.amount
        
@admin.register(WriteOffOrder)
class WriteoffOrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'placed_at'
    list_display = ['event', 'placed_at', 'amount']
    raw_id_fields = ['added_by', 'event']
    readonly_fields = ['placed_at']

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        formset.save()
        form.instance.save()  # Updates Order.amount


class SellingPriceInline(admin.TabularInline):
    model = SellingPrice
    extra = 1


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    inlines = [SellingPriceInline]
    list_display = ['organization', 'name']
    list_display_links = ['name']
    list_filter = ['organization']


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    inlines = [SellingPriceInline]
    list_display = ['organization', 'name']
    list_display_links = ['name']
    list_filter = ['organization']


@admin.register(PermanentProduct)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['organization', 'position', 'name', 'productgroup']
    list_display_links = ['name']
    list_filter = ['organization']
    list_editable = ['position']


@admin.register(RfidCard)
class RfidCardAdmin(admin.ModelAdmin):
    fields = ['registered_at', ('identifier', 'is_active'), 'user', 'managed_by']
    list_display = ['identifier', 'user', 'owner', 'is_active']
    list_filter = ['is_active', 'managed_by']
    readonly_fields = ['registered_at']
    search_fields = ['identifier', 'user__first_name', 'user__last_name', 'user__username']
    raw_id_fields = ['user']
