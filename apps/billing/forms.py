import calendar
import datetime

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.billing.models import (
    PermanentProduct, PriceGroup, ProductGroup, SellingPrice,
)
from utils.forms import AlexiaForm, _default_crispy_helper


class PermanentProductForm(forms.ModelForm):
    class Meta:
        model = PermanentProduct
        fields = ['name', 'shortcut', 'productgroup', 'position', 'text_color', 'background_color']

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


class FilterEventForm(AlexiaForm):
    helper = _default_crispy_helper(_('Export'))
    helper.attrs = {'target': '_blank'}

    now = timezone.now()
    last_day = calendar.monthrange(now.year, now.month - 1)[1]

    from_time = forms.SplitDateTimeField(
        label=_('From time'),
        initial=datetime.datetime(now.year, now.month - 1, 1),
    )
    till_time = forms.SplitDateTimeField(
        label=_('Till time'),
        initial=datetime.datetime(now.year, now.month - 1, last_day, 23, 59, 59),
    )
