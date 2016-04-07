from django.contrib.auth.models import User
from django.forms import ModelForm

from apps.organization.models import Certificate
from utils.forms import default_crispy_helper


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    helper = default_crispy_helper()


class IvaForm(ModelForm):
    class Meta:
        model = Certificate
        fields = ('file',)

    helper = default_crispy_helper()
