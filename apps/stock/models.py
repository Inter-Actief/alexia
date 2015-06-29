from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.scheduling.models import Event
from apps.organization.models import Organization


class EventConsumption(models.Model):
    """A group of consumptions. Usually, an event only has one consumption group
    but it is possible that - for some reason - different consumption groups are
    assigned to an event. This can happen in the case of an event at multiple
    locations, or for the administration of free consumptions.
    
    In the previous 'paper-full' system, this was named a 'consumption form'.
    
    event      -- The event this group belongs to
    comments   -- Comments on this group. This might be something to denote why
                  this form was opened, or what happend during the event.
    opened_at  -- The date and time at which this group was opened
    closed_at  -- The date and time at which this group was completed, i.e. when
                  no consumptions can be made anymore. Omitted if the group is 
                  still open.
    
    And, we can also access:
    
    consumptions    -- The consumptions within this consumption group.
    """
    name = models.CharField(_('name'), max_length=32, blank=False)
    event = models.ForeignKey(Event, verbose_name=_('event'))
    comments = models.TextField(_('comments'), blank=True)
    opened_at = models.DateTimeField(_('opened at'), default=timezone.now)
    closed_at = models.DateTimeField(_('closed at'), blank=True, null=True)

    def is_closed(self):
        """Boolean indicating whether the group has been closed."""
        return bool(self.closed_at)

    def __unicode__(self):
        return "%s %s" % (self.event, self.opened_at)

    class Meta:
        verbose_name = _('event consumption')
        verbose_name_plural = _('event consumptions')
        ordering = ['opened_at']


class StockProduct(models.Model):
    """A product that can be in stock. This can be bottles or barrels or the
    like, but no glasses of something from that bottle.
    
    name    -- The name of this product
    
    Access to:
    
    consumptions  -- The related consumptions of this product.
    stockcounts   -- The related stock counts of this product.
    """

    name = models.CharField(_('name'), max_length=32)
    ideal_amount = models.IntegerField(_('ideal amount'))

    def __unicode__(self):
        return self.name

    def in_stock(self):
        try:
            amount = StockProductAmount.objects.get(product=self, stockcount=self.stockcounts.latest()).amount
        except:
            amount = 0
        try:
            for cons in self.consumptions.filter(
                    used_at__gte=self.stockcounts.latest().date):  # alleen vanaf de laatste stockcount
                amount = amount - 1  # TODO iets met gewichten en glazen cola ipv flessen...
        except:
            pass

        return amount

    class Meta:
        verbose_name = _('stock product')
        verbose_name_plural = _('stock products')


class Consumption(models.Model):
    """A single consumption of a stock product within a consumption group. We
    can save the consumption of 'one' stock product, or the start and end weight
    of a barrel of beer. We can also administer at which tap we have connected
    the barrel. 
    
    product      -- The product from which was consumed
    group        -- The group at which this consumption was administered.
    used_at      -- The date and time at which this consumption was administered
    tap          -- The - optional - tap at which this consumption took place
    start_weight -- The beginning weight of the consumption product
    end_weight   -- The final weight of the consumption product
    
    If the weights aren't present, one 'unit' is assumed.
    """
    product = models.ForeignKey(StockProduct, related_name='consumptions', verbose_name=_('product'))
    group = models.ForeignKey(EventConsumption, related_name='consumptions', verbose_name=_('consumption group'))
    used_at = models.DateTimeField(_('used at'), default=timezone.now)
    tap = models.PositiveSmallIntegerField(_('tap'), blank=True, null=True)
    start_weight = models.DecimalField(_('start weight'), max_digits=5, decimal_places=2, blank=True, null=True)
    end_weight = models.DecimalField(_('end weight'), max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = _('consumption')
        verbose_name_plural = _('consumptions')


class StockCount(models.Model):
    """Representation of a count of the current stock. 
    
    organization -- The responsible organization of this stock count.
    user         -- The user who did the this stock count.
    date         -- The date (and time) of the stock count.
    is_completed -- Boolean indicating that the stock count was completed.
    comments     -- Comments on the stock count.
    products     -- The products counted in this stock count.
    """
    organization = models.ForeignKey(Organization, related_name='stockcounts', verbose_name=_('organization'))
    user = models.ForeignKey(User)
    date = models.DateTimeField(_('date'), default=timezone.now)
    is_completed = models.BooleanField(_('is completed'), default=False)
    comments = models.TextField(_('comments'), blank=True)
    products = models.ManyToManyField(StockProduct,
                                      through='StockProductAmount', related_name='stockcounts',
                                      verbose_name=_('products'), blank=True, null=True)

    class Meta:
        verbose_name = _('stock count')
        verbose_name_plural = _('stock counts')
        get_latest_by = "date"


class StockProductAmount(models.Model):
    """The intermediary class between a stock count and a stock product,
    allowing the save of the amount in stock.
    
    stockcount     -- The stock count in which the amount was determined
    product        -- The product to which the amount applies
    amount         -- The amount counted in the stock count
    """
    stockcount = models.ForeignKey(StockCount, verbose_name=_('stock count'))
    product = models.ForeignKey(StockProduct, verbose_name=_('product'))
    amount = models.PositiveIntegerField(_('amount'))

    class Meta:
        verbose_name = _('stock product amount')
        verbose_name_plural = _('stock product amounts')
