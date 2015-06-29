from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from alexia.stock.models import StockCount, StockProductAmount, EventConsumption, StockProduct
from alexia.bootstrap.forms import BootstrapModelForm


class StockCountForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(StockCountForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StockCount
        exclude = ('organization', 'user', 'date', 'products', 'is_completed',)


class StockCountAmountForm(BootstrapModelForm):
    product_id = forms.IntegerField(widget=widgets.HiddenInput())

    def __init__(self, product=None, *args, **kwargs):
        super(StockCountAmountForm, self).__init__(*args, **kwargs)
        if product:
            self.fields['product_id'].initial = product.pk
            self.prod = product

    class Meta:
        model = StockProductAmount
        exclude = ('stockcount', 'product',)


class StockProductForm(BootstrapModelForm):
    class Meta:
        model = StockProduct


class EventConsumptionForm(BootstrapModelForm):
    def __init__(self, event=None, *args, **kwargs):
        super(EventConsumptionForm, self).__init__(*args, **kwargs)
        if event:
            self.event = event
            self.fields['name'].initial = _('Event consumption #%s') % (event.eventconsumption_set.count() + 1)

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        ec = super(EventConsumptionForm, self).save(*args, **kwargs)
        ec.event = self.event
        ec.save()

    class Meta:
        model = EventConsumption
        fields = ('name',)
