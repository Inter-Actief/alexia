from django import forms
from django.utils.translation import ugettext_lazy as _

from alexia.apps.organization.models import Certificate
from alexia.apps.scheduling.models import Availability, BartenderAvailability
from alexia.core.validators import validate_username
from alexia.forms import AlexiaModelForm

from .models import Membership


class BartenderAvailabilityForm(AlexiaModelForm):
    availability = forms.ModelChoiceField(Availability.objects.none(), label=_('Availability'))

    class Meta:
        model = BartenderAvailability
        fields = ['availability']

    def __init__(self, event=None, user=None, *args, **kwargs):
        super(BartenderAvailabilityForm, self).__init__(*args, **kwargs)
        if event:
            self.event = event
            self.fields['availability'].queryset = Availability.objects.filter(organization=event.organizer)
        if user:
            self.user = user

    def save(self, *args, **kwargs):
        try:
            obj = BartenderAvailability.objects.get(event=self.event, user=self.user)
            obj.availability = self.cleaned_data['availability']
            ba = obj.save()
        except BartenderAvailability.DoesNotExist:
            ba = BartenderAvailability.objects.create(
                event=self.event,
                user=self.user,
                availability=self.cleaned_data['availability'],
            )
        return ba


class MembershipAddForm(forms.Form):
    username = forms.CharField(
        label=_('Username'),
        help_text=_('Student or employee account (e.g. s0000000 or m0000000)'),
        min_length=8,
        max_length=8,
        validators=[validate_username],
    )


class MembershipUpdateForm(forms.ModelForm):
    nickname = forms.CharField(required=False, label=_('Bartender nickname'))

    class Meta:
        model = Membership
        fields = ['is_active', 'is_tender', 'is_planner', 'is_manager', 'nickname', 'comments']


class UploadIvaForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['file']
