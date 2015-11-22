# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import PriceGroup, ProductGroup, SellingPrice, Product, \
    PermanentProduct, TemporaryProduct, Authorization, Order, Purchase, RfidCard


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 1


class RfidCardInline(admin.TabularInline):
    model = RfidCard
    extra = 1
    raw_id_fields = ('user',)
    readonly_fields = ('registered_at',)


class SellingPriceInline(admin.TabularInline):
    model = SellingPrice
    extra = 1


class PriceGroupInline(admin.TabularInline):
    model = PriceGroup
    extra = 1


class ProductGroupInline(admin.TabularInline):
    model = ProductGroup
    extra = 1


class TemporaryProductInline(admin.TabularInline):
    model = TemporaryProduct
    extra = 1


class PurchaseInline(admin.TabularInline):
    model = Purchase
    extra = 1
    raw_id_fields = ('order', 'product')
    fields = ('order', 'product', 'amount', 'price')
    createonly_fields = ('order', 'product', 'amount', 'price')
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        # Allow editing some fields only at creation time
        if obj and obj.pk:
            return self.readonly_fields + self.createonly_fields
        else:
            return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        # Orders should not be modified
        return False


class PriceGroupAdmin(admin.ModelAdmin):
    inlines = (SellingPriceInline,)
    list_display = ('name', 'organization',)
    list_filter = ('organization',)


class ProductGroupAdmin(admin.ModelAdmin):
    inlines = (SellingPriceInline,)
    list_display = ('name', 'organization',)
    list_filter = ('organization',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_permanent', 'is_temporary',)
    search_fields = ('name',)

    def has_add_permission(self, request):
        # Direct creation of products is forbidden
        return False


class PermanentProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'productgroup', 'stockproduct', 'position',)
    list_filter = ('organization', 'productgroup', 'stockproduct',)
    list_editable = ('position',)


class RfidCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'atqa', 'sak', 'uid', 'is_active',)
    list_filter = ('is_active', 'managed_by',)
    raw_id_fields = ('user',)
    readonly_fields = ('registered_at',)
    search_fields = ('atqa', 'sak', 'uid', 'user__first_name', 'user__last_name', 'user__username',)


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'start_date', 'end_date')
    list_filter = ('organization',)
    raw_id_fields = ('user',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'account')


class OrderAdmin(admin.ModelAdmin):
    inlines = (PurchaseInline,)
    date_hierarchy = 'placed_at'
    createonly_fields = ('event', 'authorization', 'placed_at',)
    list_display = ('event', 'placed_at', 'get_price')
    list_filter = ('authorization__organization',)
    raw_id_fields = ('event', 'authorization')

    def get_readonly_fields(self, request, obj=None):
        # Allow editing some fields only at creation time
        if obj and obj.pk:
            return self.readonly_fields + self.createonly_fields
        else:
            return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        # Orders should not be modified
        return False


admin.site.register(PriceGroup, PriceGroupAdmin)
admin.site.register(ProductGroup, ProductGroupAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(PermanentProduct, PermanentProductAdmin)
admin.site.register(RfidCard, RfidCardAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Order, OrderAdmin)
