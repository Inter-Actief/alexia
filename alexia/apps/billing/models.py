from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from alexia.apps.organization.models import Organization
from alexia.apps.scheduling.models import Event
from alexia.core.validators import validate_color


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
        ordering = ['organization', 'name']
        verbose_name = _('product group')
        verbose_name_plural = _('product groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('productgroup_detail', args=[self.pk])


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
        ProductGroup,
        through='SellingPrice',
        related_name='pricegroups',
        verbose_name=_('product groups'),
    )

    class Meta:
        ordering = ['organization', 'name']
        verbose_name = _('price group')
        verbose_name_plural = _('price groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pricegroup_detail', args=[self.pk])


@python_2_unicode_compatible
class SellingPrice(models.Model):
    pricegroup = models.ForeignKey(PriceGroup, models.CASCADE, verbose_name=_('price group'))
    productgroup = models.ForeignKey(ProductGroup, models.CASCADE, verbose_name=_('product group'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('pricegroup', 'productgroup')
        verbose_name = _('selling price')
        verbose_name_plural = _('selling prices')

    def __str__(self):
        return _('{product} for {price}').format(
            product=self.productgroup.name,
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
        return hasattr(self, 'permanentproduct')

    @property
    def is_temporary(self):
        return hasattr(self, 'temporaryproduct')

    def get_price(self, event):
        return self.as_leaf_class().get_price(event)

    def as_leaf_class(self):
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
    position = models.IntegerField(_('position'))

    class Meta:
        ordering = ['organization', 'position']
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

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
        models.CASCADE,
        null=True,
        related_name='temporaryproducts',
        verbose_name=_('event'),
    )
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('temporary product')
        verbose_name_plural = _('temporary products')

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name=_('user'))
    managed_by = models.ManyToManyField(Organization, verbose_name=_('managed by'))

    class Meta:
        verbose_name = _('RFID card')
        verbose_name_plural = _('RFID cards')

    def __str__(self):
        return self.identifier

    def owner(self):
        return self.user.get_full_name()
    owner.short_description = _('owner')


@python_2_unicode_compatible
class Authorization(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='authorizations',
        verbose_name=_('user'),
    )
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name='authorizations',
        verbose_name=_('organization'),
    )
    start_date = models.DateTimeField(_('start date'), default=timezone.now)
    end_date = models.DateTimeField(_('end date'), blank=True, null=True)

    class Meta:
        verbose_name = _('authorization')
        verbose_name_plural = _('authorizations')

    def __str__(self):
        return _('{user} of {organization}').format(
            user=self.user.get_full_name(),
            organization=self.organization,
        )

    def owner(self):
        return self.user.get_full_name()
    owner.short_description = _('owner')

    @classmethod
    def get_for_user_event(cls, user, event):
        authorizations = cls.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now()),
            user=user,
            organization=event.organizer,
            start_date__lte=timezone.now(),
        )

        if authorizations:
            return authorizations[0]
        else:
            return None

    def is_valid(self):
        if not self.end_date:
            return self.start_date <= timezone.now()
        else:
            return self.start_date <= timezone.now() <= self.end_date


@python_2_unicode_compatible
class Order(models.Model):
    event = models.ForeignKey(Event, models.PROTECT, related_name='orders', verbose_name=_('event'))
    authorization = models.ForeignKey(
        Authorization,
        models.PROTECT,
        related_name='orders',
        verbose_name=_('authorization'),
    )
    placed_at = models.DateTimeField(_('placed at'), default=timezone.now)
    synchronized = models.BooleanField(
        _('synchronized'),
        default=False,
        help_text=_(
            'Designates whether this transaction is imported by the organization.'
        ),
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        verbose_name=_('added by'),
        related_name='+',
    )
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2)
    rfidcard = models.ForeignKey(RfidCard, models.SET_NULL, verbose_name=_('rfid card'), blank=True, null=True)

    class Meta:
        ordering = ['-placed_at']
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return _('{user} at {time} on {event}').format(
            user=self.authorization.user.get_full_name(),
            time=self.placed_at.strftime('%H:%M'),
            event=self.event.name,
        )

    def save(self, *args, **kwargs):
        self.amount = self.get_price()
        super(Order, self).save(*args, **kwargs)

    def get_price(self):
        amount = Decimal('0.0')
        for purchase in self.purchases.all():
            amount += purchase.price
        return amount

    def debtor(self):
        return self.authorization.user.get_full_name()
    debtor.short_description = _('debtor')


@python_2_unicode_compatible
class Purchase(models.Model):
    order = models.ForeignKey(Order, models.CASCADE, related_name='purchases', verbose_name=_('order'))
    product = models.CharField(_('product'), max_length=32)
    amount = models.PositiveSmallIntegerField(_('amount'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')

    def __str__(self):
        return '%s x %s' % (self.amount, self.product)
