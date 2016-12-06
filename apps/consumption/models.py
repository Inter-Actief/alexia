from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from utils.models import InheritanceCastModel


@python_2_unicode_compatible
class ConsumptionProduct(models.Model):
    name = models.CharField(_('name'), max_length=32)

    class Meta:
        verbose_name = _('consumption product')
        verbose_name_plural = _('consumption products')

    def __str__(self):
        return self.name

    def is_weighted(self):
        return hasattr(self, 'weightconsumptionproduct')

    def weighted(self):
        return self.weightconsumptionproduct


class WeightConsumptionProduct(ConsumptionProduct):
    full_weight = models.DecimalField(_('full weight'), max_digits=4, decimal_places=1)
    empty_weight = models.DecimalField(_('empty weight'), max_digits=4, decimal_places=1)
    has_flowmeter = models.BooleanField(
        _('has flowmeter'),
        default=False,
        help_text=_('Designates wheter apart from weight, this product also uses a flowmeter.'),
    )

    class Meta:
        verbose_name = _('consumption product by weight')
        verbose_name_plural = _('consumption products by weight')
