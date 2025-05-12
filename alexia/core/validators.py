from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

color_validator = RegexValidator(
    r'^[0-9a-zA-Z]{6}$',
    _('Enter a valid hexadecimal color'),
    code='invalid',
)


def validate_color(value):
    return color_validator(value)


username_validator = RegexValidator(
    r'^[dmsx][0-9]{7}$',
    _('Enter a valid username'),
    code='invalid',
)


def validate_username(value):
    return username_validator(value)
