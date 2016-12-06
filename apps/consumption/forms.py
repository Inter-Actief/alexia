from __future__ import unicode_literals

from django.forms import ModelForm, Textarea
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from .models import ConsumptionForm, WeightEntry, UnitEntry


class ConsumptionFormForm(ModelForm):
    class Meta:
        model = ConsumptionForm
        fields = ['comments']
        widgets = {
            'comments': Textarea(attrs={'placeholder': _('Comments...'), 'rows': '4'}),
        }


WeightEntryFormSet = inlineformset_factory(
    ConsumptionForm,
    WeightEntry,
    fields=['product', 'start_weight', 'kegs_changed', 'end_weight', 'flow_start', 'flow_end'],
    max_num=3,
)


UnitEntryFormSet = inlineformset_factory(
    ConsumptionForm,
    UnitEntry,
    fields=['product', 'amount'],
)
