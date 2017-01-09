import calendar
import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from alexia.apps.billing.models import (
    PermanentProduct, PriceGroup, ProductGroup, SellingPrice,
)
from alexia.forms import default_crispy_helper


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


class FilterEventForm(forms.Form):
    helper = default_crispy_helper(_('Export'))
    helper.attrs = {'target': '_blank'}

    now = timezone.now()
    if now.month == 1:
        year = now.year - 1
        month = 12
    else:
        year = now.year
        month = now.month - 1

    from_time = forms.SplitDateTimeField(
        label=_('From time'),
        initial=datetime.datetime(year, month, 1),
    )
    till_time = forms.SplitDateTimeField(
        label=_('Till time'),
        initial=datetime.datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59),
    )
