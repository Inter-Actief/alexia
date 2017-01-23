import calendar
import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from alexia.apps.billing.models import (
    PermanentProduct, PriceGroup, ProductGroup, SellingPrice,
)
from alexia.forms import AlexiaForm


class PermanentProductForm(forms.ModelForm):
    class Meta:
        model = PermanentProduct
        fields = ['name', 'productgroup', 'position', 'text_color', 'background_color']

    def __init__(self, organization, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)


class SellingPriceForm(forms.ModelForm):
    class Meta:
        model = SellingPrice
        fields = ['pricegroup', 'productgroup', 'price']

    def __init__(self, organization, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['pricegroup'].queryset = PriceGroup.objects.filter(organization=organization)
        self.fields['productgroup'].queryset = ProductGroup.objects.filter(organization=organization)


def get_previous_month(start=True):
    now = timezone.now()
    year = now.year - 1 if now.month == 1 else now.year
    month = 12 if now.month == 1 else now.month - 1

    if start:
        return datetime.datetime(year, month, 1)
    return datetime.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)


def get_previous_month_end():
    return get_previous_month(False)


class FilterEventForm(AlexiaForm):
    submit_text = _('Export')

    from_time = forms.SplitDateTimeField(label=_('From time'), initial=get_previous_month)
    till_time = forms.SplitDateTimeField(label=_('Till time'), initial=get_previous_month_end)

    def get_helper(self):
        helper = super(FilterEventForm, self).get_helper()
        helper.attrs = {'target': '_blank'}
        return helper
