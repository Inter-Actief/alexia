from __future__ import unicode_literals

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from apps.organization.models import Organization
from apps.scheduling.models import Event
from apps.stock.models import StockProduct
from utils.validators import validate_color


@python_2_unicode_compatible
class PriceGroup(models.Model):
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='pricegroups',
        verbose_name=_('organization'),
    )
    name = models.CharField(_('name'), max_length=32)
    productgroups = models.ManyToManyField(
        'ProductGroup',
        through='SellingPrice',
        related_name='pricegroups',
        verbose_name=_('product groups'),
    )

    class Meta:
        verbose_name = _('price group')
        verbose_name_plural = _('price groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pricegroup_detail', args=[self.pk])


@python_2_unicode_compatible
class ProductGroup(models.Model):
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='productgroups',
        verbose_name=_('organization'),
    )
    name = models.CharField(_('name'), max_length=32)

    class Meta:
        verbose_name = _('product group')
        verbose_name_plural = _('product groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('productgroup_detail', args=[self.pk])


@python_2_unicode_compatible
class SellingPrice(models.Model):
    pricegroup = models.ForeignKey(PriceGroup, models.CASCADE, verbose_name=_('price group'))
    productgroup = models.ForeignKey(ProductGroup, models.CASCADE, verbose_name=_('product group'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('pricegroup', 'productgroup')

    def __str__(self):
        return _('{pricegroup}: {productgroup} for {price}').format(
            pricegroup=self.pricegroup,
            productgroup=self.productgroup,
            price=self.price,
        )

    def get_absolute_url(self):
        return self.pricegroup.get_absolute_url()


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(_('name'), max_length=32)
    text_color = models.CharField(
        verbose_name=_('Text color'),
        blank=True,
        help_text=_('Text color for Juliana'),
        max_length=6,
        validators=[validate_color],
    )
    background_color = models.CharField(
        verbose_name=_('Background color'),
        blank=True,
        help_text=_('Background color for Juliana'),
        max_length=6,
        validators=[validate_color],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

    @property
    def is_permanent(self):
        """Indicates whether this is a PermanentProduct"""
        return hasattr(self, 'permanentproduct')

    @property
    def is_temporary(self):
        """Indicates whether this is a TemporaryProduct"""
        return hasattr(self, 'temporaryproduct')

    def get_price(self, event):
        """Gets the price for a given event."""
        return self.as_leaf_class().get_price(event)

    def as_leaf_class(self):
        """
        Return the leaf class object of this object.
        :return: This object as PermanentProduct or TemporaryProduct
        :rtype: PermanentProduct|TemporaryProduct
        """
        if self.is_permanent:
            return self.permanentproduct
        elif self.is_temporary:
            return self.temporaryproduct
        else:
            raise Exception('Product is neither permament nor temporary')


class PermanentProduct(Product):
    productgroup = models.ForeignKey(ProductGroup, models.CASCADE, verbose_name=_('product group'))
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='products',
        verbose_name=_('organization'),
    )
    stockproduct = models.ForeignKey(StockProduct, verbose_name=_('stock product'), blank=True, null=True)
    position = models.IntegerField(_('position'))

    class Meta:
        ordering = ['organization', 'productgroup', 'position']

    def get_absolute_url(self):
        return reverse('permanentproduct_detail', args=[self.pk])

    def is_permanent(self):
        return True

    def is_temporary(self):
        return False

    def get_price(self, event):
        productgroup = self.productgroup
        pricegroup = event.pricegroup
        try:
            sp = SellingPrice.objects.get(pricegroup=pricegroup, productgroup=productgroup)
            return sp.price
        except SellingPrice.DoesNotExist:
            # No price defined for this event
            return None


class TemporaryProduct(Product):
    event = models.ForeignKey(
        Event,
        models.SET_NULL,
        null=True,
        related_name='temporaryproducts',
        verbose_name=_('event'),
    )
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    def get_absolute_url(self):
        return reverse('temporaryproduct_detail', args=[self.pk])

    def is_permanent(self):
        return True

    def is_temporary(self):
        return False

    def get_price(self, event):
        return self.temporaryproduct.price


@python_2_unicode_compatible
class RfidCard(models.Model):
    identifier = models.CharField(_('identifier'), unique=True, max_length=50)
    is_active = models.BooleanField(_('is active'), default=False)
    registered_at = models.DateTimeField(_('registered at'), default=timezone.now)
    user = models.ForeignKey(User, models.CASCADE, related_name='rfids', verbose_name=_('user'))
    managed_by = models.ManyToManyField(Organization)

    class Meta:
        verbose_name = _('RFID card')
        verbose_name_plural = _('RFID cards')

    def __str__(self):
        return self.identifier


@python_2_unicode_compatible
class Authorization(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='authorizations', verbose_name=_('user'))
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='authorizations',
        verbose_name=_('organization'),
    )
    start_date = models.DateTimeField(_('start date'), default=timezone.now)
    end_date = models.DateTimeField(_('end date'), blank=True, null=True)
    account = models.CharField(_('account'), max_length=32, blank=True)

    class Meta:
        verbose_name = _('authorization')
        verbose_name_plural = _('authorizations')

    def __str__(self):
        return "%s at %s" % (self.user, self.organization)

    @classmethod
    def get_for_user_event(cls, user, event):
        """Get authorization if given user and event, if any.

        Returns Authorization object or None."""

        authorizations = cls.objects.filter(Q(end_date__isnull=True) | Q(end_date__gte=timezone.now()), user=user,
                                            organization=event.organizer, start_date__lte=timezone.now())

        if authorizations:
            return authorizations[0]
        else:
            return None

    def is_valid(self):
        """Returns whether this authorization is currently valid."""
        if not self.end_date:
            return self.start_date <= timezone.now()
        else:
            return self.start_date <= timezone.now() <= self.end_date


class Order(models.Model):
    event = models.ForeignKey(Event, models.PROTECT, related_name='orders', verbose_name=_('event'))
    authorization = models.ForeignKey(
        Authorization,
        models.PROTECT,
        related_name='orders',
        verbose_name=_('authorization'),
    )
    placed_at = models.DateTimeField(_('placed at'), default=timezone.now)
    synchronized = models.BooleanField(_('synchronized'), default=False)
    added_by = models.ForeignKey(User, models.PROTECT, verbose_name=_('added by'), related_name='+')
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2)
    rfidcard = models.ForeignKey(RfidCard, models.PROTECT, verbose_name=_('rfid card'), blank=True, null=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def save(self, *args, **kwargs):
        self.amount = self.get_price()
        super(Order, self).save(*args, **kwargs)

    def is_collected(self):
        """Returns whether the order has been collected."""
        return bool(self.collected_at)

    def get_price(self):
        """Get the total amount of this order."""

        amount = Decimal('0.0')
        for purchase in self.purchases.all():
            amount += purchase.price
        return amount

    get_price.short_description = _('price')


class Purchase(models.Model):
    order = models.ForeignKey(Order, models.PROTECT, related_name='purchases', verbose_name=_('order'))
    product = models.ForeignKey(Product, models.PROTECT, related_name='purchases', verbose_name=_('product'))
    amount = models.IntegerField(_('amount'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')
