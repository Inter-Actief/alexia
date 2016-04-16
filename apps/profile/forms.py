from django.contrib.auth.models import User

from apps.organization.models import Certificate
from utils.forms import AlexiaModelForm


class ProfileForm(AlexiaModelForm):
    class Meta:
        model = User
        fields = ['email']


class IvaForm(AlexiaModelForm):
    class Meta:
        model = Certificate
        fields = ['file']
