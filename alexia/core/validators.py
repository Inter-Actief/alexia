from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


color_validator = RegexValidator(
    r'^[0-9a-zA-Z]{6}$',
    _('Enter a valid hexadecimal color'),
    code='invalid',
)


def validate_color(value):
    return color_validator(value)


radius_username_validator = RegexValidator(
    r'^[ms][0-9]{7}$',
    _('Enter a valid RADIUS username'),
    code='invalid',
)


def validate_radius_usernam(value):
    return radius_username_validator(value)
