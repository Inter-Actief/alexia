from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils import timezone
from django.utils.translation import ugettext as _

from apps.organization.models import Organization, Location
from apps.scheduling.models import Event, StandardReservation, MailTemplate
from utils.mail import mail


class EventForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        Organization.public_objects.all(),
        widget=widgets.CheckboxSelectMultiple,
        label=_("Participants"))
    location = forms.ModelMultipleChoiceField(
        Location.objects.all(), widget=widgets.CheckboxSelectMultiple,
        label=_("Location"))
    starts_at = forms.SplitDateTimeField()
    ends_at = forms.SplitDateTimeField()

    def __init__(self, request=None, *args, **kwargs):
        """Overrides the default init to select initial values based on the
        primary organization, and select the right queryset for the pricegroup.
        The queryset will be updated to the form via AJAX.
        """

        super(EventForm, self).__init__(*args, **kwargs)

        if request:
            primary_organization = request.organization
            self.fields['participants'].initial = [primary_organization]
            # self.fields['pricegroup'].queryset =
            # PriceGroup.objects.filter(organization=primary_organization)
            self.fields['pricegroup'].choices = self.organize_pricegroups(
                [primary_organization.pk])

        if 'instance' in kwargs and kwargs['instance'].organizer:
            try:
                # self.fields['pricegroup'].queryset =
                # PriceGroup.objects.filter(
                # organization=kwargs['data']['organizer'])
                self.fields['pricegroup'].choices = self.organize_pricegroups(
                    [kwargs['instance'].organizer.pk])
            except:
                pass

    def organize_pricegroups(self, organizations):
        organizations = Organization.objects.filter(id__in=organizations)

        result = []
        for organization in organizations:
            # Get all the pricegroups
            pricegroups = []
            for pricegroup in organization.pricegroups.all():
                pricegroups.append([pricegroup.pk, pricegroup.name])

            # Append them
            result.append([organization.name, pricegroups])

        return result

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        starts_at = cleaned_data.get('starts_at')
        ends_at = cleaned_data.get('ends_at')
        locations = cleaned_data.get('location')

        if starts_at and ends_at and starts_at > ends_at:
            raise ValidationError(
                _("The start time is earlier than the end time!"))

        if starts_at and ends_at and locations:
            for location in locations:
                if location.prevent_conflicting_events:
                    conf_events = Event.conflicting_events(starts_at, ends_at,
                                                           location)
                    if self.instance:
                        conf_events = conf_events.exclude(pk=self.instance.pk)
                    if conf_events.exists():
                        raise ValidationError(
                            _("There is an event in %(location)s already!") % {'location': location.name})

        return cleaned_data

    def save(self, organizer=None, *args, **kwargs):
        event = super(EventForm, self).save(*args, **kwargs)
        if not organizer:
            organizer = event.organizer
        # Mail voor standardreservations
        for reservation in StandardReservation.objects.occuring_at(
                self.cleaned_data['starts_at'], self.cleaned_data['ends_at']):
            if reservation.location in self.cleaned_data['location'] and \
                    not reservation.organization == organizer:
                try:
                    mt = MailTemplate.objects.get(
                        organization=reservation.organization,
                        name="reservations")
                    if mt.is_active:
                        addressees = reservation.organization.managers.all()
                        mail(settings.EMAIL_FROM, addressees, mt.subject,
                             mt.template, extraattrs={'event': event})
                except MailTemplate.DoesNotExist:
                    pass  # Dan maar geen mail...

        return event

    class Meta:
        model = Event
        fields = ('participants', 'name', 'description', 'starts_at',
                  'ends_at', 'is_closed', 'option', 'is_risky', 'location',
                  'kegs', 'pricegroup', 'tender_comments')

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(Submit('submit', _('Save')))


class EditEventForm(EventForm):
    def save(self, organizer=None, *args, **kwargs):
        return super(EventForm, self).save(*args, **kwargs)


class StandardReservationForm(forms.ModelForm):
    class Meta:
        model = StandardReservation
        fields = ('organization', 'start_day', 'end_day', 'location')


class FilterEventForm(forms.Form):
    location = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(), initial=Location.objects.all(),
        widget=widgets.CheckboxSelectMultiple, label=_("Locations"),
        required=False)
    organizer = forms.ModelChoiceField(required=False,
                                       queryset=Organization.objects, label=_("Organization"))
    from_time = forms.DateTimeField(label=_("From time"),
                                    initial=timezone.now, widget=widgets.SplitDateTimeWidget)
    till_time = forms.DateTimeField(label=_("Till time"),
                                    widget=widgets.SplitDateTimeWidget, required=False)

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_method = 'GET'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(Submit('submit', _('Filter')))

    def __init__(self, *args, **kwargs):
        super(FilterEventForm, self).__init__(*args, **kwargs)

        # Workaround for https://github.com/maraujop/django-crispy-forms/issues/303
        self.fields['location'].choices = self.fields['location'].choices
