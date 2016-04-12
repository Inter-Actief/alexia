from django import forms
from django.contrib.auth.models import User

from apps.organization.models import Certificate
from utils.forms import BootstrapFormMixin


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class IvaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['file']
