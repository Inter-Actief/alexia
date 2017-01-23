from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import Form, ModelForm
from django.utils.translation import ugettext as _


class BaseCrispyFormMixin(object):
    submit_text = None

    def get_helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-10'
        helper.add_input(Submit('submit', self.get_submit_text()))
        return helper

    def get_submit_text(self):
        if self.submit_text:
            return self.submit_text
        else:
            return _('Save')


class CrispyFormMixin(BaseCrispyFormMixin):
    def get_form(self, form_class=None):
        form = super(CrispyFormMixin, self).get_form(form_class)
        form.helper = self.get_helper()
        return form


class BootstrapFormMixin(BaseCrispyFormMixin):
    def __init__(self, *args, **kwargs):
        self.helper = self.get_helper()
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)


class AlexiaForm(BootstrapFormMixin, Form):
    pass


class AlexiaModelForm(BootstrapFormMixin, ModelForm):
    pass
