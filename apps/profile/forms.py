from django import forms
from django.contrib.auth.models import User

from apps.organization.models import Certificate
from utils.forms import default_crispy_helper


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    helper = default_crispy_helper()


class IvaForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['file']

    helper = default_crispy_helper()
