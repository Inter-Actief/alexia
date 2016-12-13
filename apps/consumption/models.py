from __future__ import unicode_literals

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from apps.scheduling.models import Event


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


@python_2_unicode_compatible
class ConsumptionForm(models.Model):
    event = models.OneToOneField(
        Event,
        models.CASCADE,
        verbose_name=_('event'),
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        verbose_name=_('completed by'),
    )
    completed_at = models.DateTimeField(_('completed at'), null=True)
    comments = models.TextField(_('comments'), blank=True)

    class Meta:
        verbose_name = _('consumption form')
        verbose_name_plural = _('consumption forms')

    def __str__(self):
        return self.event.name

    def issues(self):
        issues = {
            'errors': [],
            'warnings': [],
        }

        # Validate weight entries
        for e in self.weightentry_set.all():
            # Has end weight?
            if not e.end_weight:
                issues['errors'].append(_('%(product)s has no end weight.') % {'product': e.product})
            # Has flowmeter end?
            if e.product.has_flowmeter and not e.flow_end:
                issues['errors'].append(_('%(product)s has no flowmeter end.') % {'product': e.product})
            if e.product.has_flowmeter and e.is_doubtful():
                issues['warnings'].append(_('%(product)s weight and flowmeter differences are doubtful.') % {
                    'product': e.product
                })
        # Are there any entries?
        if not self.weightentry_set.count() and not self.unitentry_set.count():
            issues['errors'].append(_('This consumption form has no entries.'))

        self._issues = issues
        return issues

    def has_issues(self):
        if not hasattr(self, '_issues'):
            self._issues = self.issues()
        return bool(len(self._issues['errors']) or len(self._issues['warnings']))

    def is_valid(self):
        if not hasattr(self, '_issues'):
            self._issues = self.issues()
        return not bool(len(self._issues['errors']))

    def is_completed(self):
        return bool(self.completed_by or self.completed_at)


class Entry(models.Model):
    consumption_form = models.ForeignKey(
        ConsumptionForm,
        models.CASCADE,
        verbose_name=_('consumption_form'),
    )

    class Meta:
        abstract = True


@python_2_unicode_compatible
class WeightEntry(Entry):
    product = models.ForeignKey(
        WeightConsumptionProduct,
        models.PROTECT,
        verbose_name=_('product'),
    )
    start_weight = models.DecimalField(_('starting weight'), max_digits=4, decimal_places=1)
    end_weight = models.DecimalField(_('end weight'), max_digits=4, decimal_places=1, blank=True, null=True)
    kegs_changed = models.PositiveSmallIntegerField(_('kegs changed'), default=0)
    flow_start = models.DecimalField(_('flowmeter start'), max_digits=6, decimal_places=1, blank=True, null=True)
    flow_end = models.DecimalField(_('flowmeter end'), max_digits=6, decimal_places=1, blank=True, null=True)

    class Meta:
        verbose_name = _('weight entry')
        verbose_name_plural = _('weight entries')

    def __str__(self):
        return str(self.product)

    def total(self):
        if not self.end_weight:
            return False

        # No kegs changed?
        if self.kegs_changed == 0:
            return self.start_weight - self.end_weight

        # First and last keg
        total = self.start_weight - self.product.empty_weight
        total += self.product.full_weight - self.end_weight
        # Everything inbetween are whole kegs
        total += (self.kegs_changed - 1) * (self.product.full_weight - self.product.empty_weight)

        return total

    def is_doubtful(self):
        if not self.end_weight or not self.flow_end:
            return False

        weight_total = self.total()
        flow_total = self.flow_end - self.flow_start
        change_percentage = abs(((weight_total - flow_total) / flow_total) * 100)

        return bool(change_percentage >= 25)


@python_2_unicode_compatible
class UnitEntry(Entry):
    product = models.ForeignKey(
        ConsumptionProduct,
        models.PROTECT,
        verbose_name=_('product'),
    )
    amount = models.PositiveSmallIntegerField(_('amount'), validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _('unit entry')
        verbose_name_plural = _('unit entries')

    def __str__(self):
        return str(self.product)
