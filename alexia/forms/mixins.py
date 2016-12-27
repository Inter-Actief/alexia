from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import Form, ModelForm
from django.utils.translation import ugettext as _


def default_crispy_helper(submit_text=None):
    if not submit_text:
        submit_text = _('Save')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-10 col-lg-8'
    helper.add_input(Submit('submit', submit_text))
    return helper


class BootstrapFormMixin:
    helper = default_crispy_helper()


class AlexiaForm(BootstrapFormMixin, Form):
    pass


class AlexiaModelForm(BootstrapFormMixin, ModelForm):
    pass


class CrispyFormMixin(object):
    """
    Mixin to add Crispy form helper.
    """
    def get_form(self, form_class=None):
        form = super(CrispyFormMixin, self).get_form(form_class)
        form.helper = default_crispy_helper()
        return form
