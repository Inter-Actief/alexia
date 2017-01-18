from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Authorization, Order, PermanentProduct, PriceGroup, ProductGroup, Purchase,
    RfidCard, SellingPrice, TemporaryProduct,
)


class AuthorizationInline(admin.TabularInline):
    model = Authorization
    extra = 0
    exclude = ['account']


class RfidCardInline(admin.TabularInline):
    model = RfidCard
    extra = 0
    readonly_fields = ('registered_at',)
    raw_id_fields = ('managed_by',)


class PurchaseInline(admin.TabularInline):
    model = Purchase
    can_delete = False


class SellingPriceInline(admin.TabularInline):
    model = SellingPrice
    extra = 1


class TemporaryProductInline(admin.TabularInline):
    model = TemporaryProduct


def _user_full_name(obj):
    return obj.user.get_full_name()


_user_full_name.short_description = _('Owner')


@admin.register(PermanentProduct)
class PermanentProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'productgroup', 'position')
    list_filter = ('organization',)
    list_editable = ('position',)


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    inlines = [
        SellingPriceInline,
    ]
    list_display = ('name', 'organization',)
    list_filter = ('organization',)
    search_fields = ('name',)


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    inlines = [
        SellingPriceInline,
    ]
    list_display = ('name', 'organization',)
    list_filter = ('organization',)
    search_fields = ('name',)


@admin.register(RfidCard)
class RfidCardAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'user', _user_full_name, 'is_active')
    list_filter = ('is_active', 'managed_by')
    readonly_fields = ['registered_at']
    search_fields = ('identifier', 'user__first_name', 'user__last_name', 'user__username')
    fields = ['identifier', 'user', 'managed_by', 'is_active', 'registered_at']
    raw_id_fields = ('user',)


@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('user', 'organization', ('start_date', 'end_date'), 'account'),
        }),
    )
    list_display = ('user', _user_full_name, 'organization', 'start_date', 'end_date')
    list_filter = ('organization', 'start_date', 'end_date')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'account')
    raw_id_fields = ('user',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (PurchaseInline,)
    add_fields = ['event', 'authorization', 'added_by', 'placed_at', 'rfidcard']
    fields = ['event', 'authorization', 'placed_at', 'rfidcard', 'added_by']
    date_hierarchy = 'placed_at'
    createonly_fields = ('event', 'authorization', 'placed_at')
    readonly_fields = ('placed_at',)
    list_display = ('event', 'user_full_name', 'placed_at', 'get_price')
    list_filter = ('authorization__organization', 'placed_at')
    raw_id_fields = ('added_by', 'authorization', 'event', 'rfidcard')
    search_fields = ('authorization__user__first_name', 'authorization__user__last_name',
                     'authorization__user__username')

    def user_full_name(self, obj):
        return obj.authorization.user.get_full_name()
    user_full_name.short_description = _('Debtor')

    def get_fields(self, request, obj=None):
        if not obj:
            return self.add_fields
        return super(OrderAdmin, self).get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            return self.readonly_fields + self.createonly_fields
        return super(OrderAdmin, self).get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False
