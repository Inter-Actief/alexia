from decimal import Decimal

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.scheduling.models import Event
from apps.organization.models import Organization
from apps.stock.models import StockProduct


class PriceGroup(models.Model):
    """A price group is a group of prices belonging to product groups.
    
    organization     -- The organization to which the group belongs
    name             -- The name of the group
    productgroups    -- The product groups for which a price has been set
    
    We also know:
    
    events        -- Events associated with this price group.
    
    """

    organization = models.ForeignKey(Organization, related_name='pricegroups', verbose_name=_('organization'))
    name = models.CharField(_('name'), max_length=32)
    productgroups = models.ManyToManyField('ProductGroup', through='SellingPrice', related_name='pricegroups',
                                           verbose_name=_('product groups'))

    class Meta:
        verbose_name = _('price group')
        verbose_name_plural = _('price groups')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pricegroup_detail', args=[self.pk])


class ProductGroup(models.Model):
    """A product group is a group to which permanent products belong. All 
    organizations specify their own product groups and link their products to 
    them.
    
    organization     -- The organization to which the group belongs
    name             -- The name of the group
    
    And:
    
    pricegroups    -- The price groups for which this product group has a price
    """

    organization = models.ForeignKey(Organization, related_name='productgroups', verbose_name=_('organization'))
    name = models.CharField(_('name'), max_length=32)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('productgroup_detail', args=[self.pk])

    class Meta:
        verbose_name = _('product group')
        verbose_name_plural = _('product groups')


class SellingPrice(models.Model):
    """The intermediary class between price groups and product groups. This is
    what it is all about: this is the price of a product group within a specific
    price group.
    
    pricegroup   -- The price group belonging to this price.
    productgroup -- The product group belonging to this price.
    price        -- The price of the price and product groups.
    """
    pricegroup = models.ForeignKey(PriceGroup, verbose_name=_('price group'))
    productgroup = models.ForeignKey(ProductGroup, verbose_name=_('product group'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    def __unicode__(self):
        return _(u'{pricegroup}: {productgroup} for {price}').format(pricegroup=self.pricegroup,
                                                                     productgroup=self.productgroup,
                                                                     price=self.price)

    def get_absolute_url(self):
        return self.pricegroup.get_absolute_url()

    class Meta:
        unique_together = (('pricegroup', 'productgroup'),)


class Product(models.Model):
    """A product that can be sold on an event.
    
    name  -- The name of the product.
    
    
    purchases    -- The purchases placed for this product
    """

    name = models.CharField(_('name'), max_length=32)
    text_color = models.CharField(verbose_name=_('Text color'), blank=True,
                                  help_text=_('Text color for Juliana'), max_length=6,
                                  validators=[RegexValidator(regex=r'^[0-9a-zA-Z]{6}$',
                                                             message=_('Enter a valid hexadecimal color'))])
    background_color = models.CharField(verbose_name=_('Background color'), blank=True,
                                        help_text=_('Background color for Juliana'), max_length=6,
                                        validators=[RegexValidator(regex=r'^[0-9a-zA-Z]{6}$',
                                                                   message=_('Enter a valid hexadecimal color'))])

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

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])


class PermanentProduct(Product):
    """A product that is permanently present  for an organization.
    
    productgroup -- The product group to which this product belongs.
    organization -- The organization to which this product belongs.
    stockproduct -- If - and only if - the permanent product maps directly to a
                    stock product, this should refer to that product.
    """
    productgroup = models.ForeignKey(ProductGroup, verbose_name=_('product group'))
    organization = models.ForeignKey(Organization, related_name='products', verbose_name=_('organization'))
    stockproduct = models.ForeignKey(StockProduct, verbose_name=_('stock product'), blank=True, null=True)
    position = models.IntegerField(verbose_name=_('position'))

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

    def get_absolute_url(self):
        return reverse('permanentproduct_detail', args=[self.pk])

    class Meta:
        ordering = ['organization', 'productgroup', 'position']


class TemporaryProduct(Product):
    """A product that only exists for one event.
    
    event   -- The event this product belongs to.
    price   -- The price of this product.
    """
    event = models.ForeignKey(Event, related_name='temporaryproducts', verbose_name=_('event'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    def is_permanent(self):
        return True

    def is_temporary(self):
        return False

    def get_price(self, event):
        return self.temporaryproduct.price

    def get_absolute_url(self):
        return reverse('temporaryproduct_detail', args=[self.pk])


class RfidCard(models.Model):
    """A representation of an RFID card, which belongs to some profile.
    
    atqa          -- ATQA of this RFID card (hexadecimal lowercase string, no colons, may be empty as a wildcard)
    sak           -- SAK of this RFID card (hexadecimal lowercase string, no colons, may be empty as a wildcard)
    uid           -- UID of this RFID card (hexadecimal lowercase string, no colons)
    is_active     -- Boolean indicating whether this card has been activated.
    registered_at -- Date and time at which the card was registered.
    profile       -- The user to which this card belongs.
    """

    atqa = models.CharField(_('ATQA'), max_length=16, default="", blank=True)
    sak = models.CharField(_('SAK'), max_length=16, default="", blank=True)
    uid = models.CharField(_('UID'), max_length=32)
    is_active = models.BooleanField(_('is active'), default=False)
    registered_at = models.DateTimeField(_('registered at'), default=timezone.now)
    user = models.ForeignKey(User, related_name='rfids', verbose_name=_('user'))
    managed_by = models.ManyToManyField(Organization)

    def __unicode__(self):
        return "RfidCard(%s, %s, %s)" % (self.atqa, self.sak, self.uid)

    class Meta:
        verbose_name = _('RFID card')
        verbose_name_plural = _('RFID cards')


class Authorization(models.Model):
    """An authorization to place orders at a specific organization. The
    authorization is only valid between the start and end date.
    
    user         -- The user that is authorized
    organization -- The organization at which the authorization is signed
    start_date   -- The start date (and time) of the authorization.
    end_date     -- The end date (and time) of the autorization, if any
    account      -- The bank account for which the authorization is valid.
                    May be omitted if the organization wishes not to use it.
    """

    user = models.ForeignKey(User, related_name='authorizations', verbose_name=_('user'))
    organization = models.ForeignKey(Organization, related_name='authorizations', verbose_name=_('organization'))
    start_date = models.DateTimeField(_('start date'), default=timezone.now)
    end_date = models.DateTimeField(_('end date'), blank=True, null=True)
    account = models.CharField(_('account'), max_length=32, blank=True)

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

    def __unicode__(self):
        return u"%s at %s" % (self.user, self.organization)

    class Meta:
        verbose_name = _('authorization')
        verbose_name_plural = _('authorizations')


class Order(models.Model):
    """A order is a set of purchases at a specific event.
    
    event        -- The event at which the order was placed.
    placed_at    -- The date (and time) at which the order was placed
    purchases    -- The purchases placed in this order
    """
    event = models.ForeignKey(Event, related_name='orders', verbose_name=_('event'))
    authorization = models.ForeignKey(Authorization, related_name='orders', verbose_name=_('authorization'))
    placed_at = models.DateTimeField(_('placed at'), default=timezone.now)
    synchronized = models.BooleanField(_('synchronized'), default=False)
    added_by = models.ForeignKey(User, verbose_name=_('added by'), related_name='+')
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2)
    rfidcard = models.ForeignKey(RfidCard, verbose_name=_('rfid card'), blank=True, null=True)

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

    def save(self, *args, **kwargs):
        self.amount = self.get_price()
        super(Order, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class Purchase(models.Model):
    """An order item, or a purchase of a specific product.
    
    order   -- The order at which the purchase was placed.
    product -- The product at which the purchase was placed.
    amount  -- The amount of the product purchased
    price   -- The total price of the purchase
    """

    order = models.ForeignKey(Order, related_name='purchases', verbose_name=_('order'))
    product = models.ForeignKey(Product, related_name='purchases', verbose_name=_('product'))
    amount = models.IntegerField(_('amount'))
    price = models.DecimalField(_('price'), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')
