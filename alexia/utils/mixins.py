from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from alexia.forms import default_crispy_helper


class OrganizationFilterMixin(object):
    """
    Mixin for SingleObjectMixin and MultipleObjectMixin to select only objects
    belonging to the current organization.
    """

    def get_queryset(self):
        return super(OrganizationFilterMixin, self).get_queryset().filter(organization=self.request.organization)


class EventOrganizerFilterMixin(object):
    """
    Mixin for SingleObjectMixin and MultipleObjectMixin to select only objects
    belonging to events organized by the current organization.
    """

    def get_queryset(self):
        return super(EventOrganizerFilterMixin, self).get_queryset().filter(event__organizer=self.request.organization)


class BaseFixedValueCreateView(ModelFormMixin, ProcessFormView):
    """
    Base view for creating an new object instance with some default values.

    Override get_instance to provide defaults.

    Using this base class requires subclassing to provide a response mixin.
    """

    def get_instance(self):
        """
        Override this method to create an instance with default values.
        """
        return self.model()

    def get(self, request, *args, **kwargs):
        self.object = self.get_instance()
        return super(BaseFixedValueCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_instance()
        return super(BaseFixedValueCreateView, self).post(request, *args, **kwargs)


class FixedValueCreateView(SingleObjectTemplateResponseMixin, BaseFixedValueCreateView):
    """
    View for creating a new object instance with some default values,
    with a response rendered by template.

    Override get_instance to provide defaults.
    """
    template_name_suffix = '_form'


class CreateViewForOrganization(FixedValueCreateView):
    """
    View for creating a new object instance with the current organization as default for the organization field,
    """

    def get_instance(self):
        return self.model(organization=self.request.organization)


class OrganizationFormMixin(object):
    """
    Mixin to create form with current organization as parameter.
    """

    def get_form_kwargs(self):
        kwargs = super(OrganizationFormMixin, self).get_form_kwargs()
        kwargs['organization'] = self.request.organization
        return kwargs


class CrispyFormMixin(object):
    """
    Mixin to add Crispy form helper.
    """

    def get_form(self, form_class=None):
        form = super(CrispyFormMixin, self).get_form(form_class)

        form.helper = default_crispy_helper()

        return form
