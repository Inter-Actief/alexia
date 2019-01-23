from django import forms
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from alexia.apps.organization.models import Location, Organization
from alexia.forms import AlexiaForm, AlexiaModelForm

from .models import Event


class EventForm(AlexiaModelForm):
    class Meta:
        model = Event
        fields = ['participants', 'name', 'description', 'starts_at', 'ends_at', 'is_closed', 'option', 'is_risky',
                  'location', 'kegs', 'pricegroup', 'tender_comments']
        field_classes = {
            'starts_at': forms.SplitDateTimeField,
            'ends_at': forms.SplitDateTimeField,
        }
        widgets = {
            'participants': forms.CheckboxSelectMultiple,
            'location': forms.CheckboxSelectMultiple,
        }

    def __init__(self, organization, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['pricegroup'].queryset = organization.pricegroups

    def clean_ends_at(self):
        starts_at = self.cleaned_data.get('starts_at')
        ends_at = self.cleaned_data.get('ends_at')
        if starts_at and ends_at and starts_at > ends_at:
            raise forms.ValidationError(
                ugettext('The end time is earlier than the start time.'),
                code='invalid',
            )
        return ends_at

    def clean_location(self):
        starts_at = self.cleaned_data.get('starts_at')
        ends_at = self.cleaned_data.get('ends_at')
        locations = self.cleaned_data.get('location')
        if starts_at and ends_at and locations:
            for location in locations:
                if location.prevent_conflicting_events:
                    conflicting_events = Event.conflicting_events(starts_at, ends_at, location)
                    if self.instance:
                        conflicting_events = conflicting_events.exclude(pk=self.instance.pk)
                    if conflicting_events.exists():
                        raise forms.ValidationError(
                            ugettext('There is already an event in %(location)s.'),
                            code='conflicting_event',
                            params={'location': location},
                        )
        return locations


class FilterEventForm(AlexiaForm):
    submit_text = _('Filter')

    location = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        initial=Location.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_('Locations'),
        required=False,
    )
    organizer = forms.ModelChoiceField(required=False, queryset=Organization.objects, label=_('Organization'))
    from_time = forms.SplitDateTimeField(label=_('From time'), initial=timezone.now, required=False)
    till_time = forms.SplitDateTimeField(label=_('Till time'), required=False)
    meetings_only = forms.BooleanField(label=_('Meetings only'), required=False)

    def get_helper(self):
        helper = super(FilterEventForm, self).get_helper()
        helper.form_method = 'GET'
        return helper
