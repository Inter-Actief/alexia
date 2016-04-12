from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _

from apps.organization.models import Membership
from apps.scheduling.models import BartenderAvailability, Availability
from utils.forms import BootstrapFormMixin


class BartenderAvailabilityForm(BootstrapFormMixin, forms.ModelForm):
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
            ba = BartenderAvailability.objects.create(event=self.event, user=self.user,
                                                      availability=self.cleaned_data['availability'])
        return ba


class MembershipAddForm(BootstrapFormMixin, forms.Form):
    username = forms.CharField(label=_('RADIUS username'),
                               help_text=_('Student or employee account'), min_length=8, max_length=8,
                               validators=[RegexValidator(regex=r'^[ms][0-9]{7}$',
                                                          message=_('Enter a valid RADIUS username'))])


class MembershipEditForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['is_tender', 'is_planner', 'is_manager', 'comments']


class CreateUserForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
