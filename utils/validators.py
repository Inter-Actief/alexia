from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


color_validator = RegexValidator(
    r'^[0-9a-zA-Z]{6}$',
    _('Enter a valid hexadecimal color'),
    'invalid',
)


def validate_color(value):
    return color_validator(value)
