import calendar
import datetime

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from wkhtmltopdf.views import PDFTemplateResponse, PDFTemplateView

from alexia.apps.organization.models import Organization
from alexia.apps.scheduling.models import Event
from alexia.auth.mixins import FoundationManagerRequiredMixin
from alexia.forms import CrispyFormMixin

from .forms import (
    ConsumptionFormConfirmationForm, ConsumptionFormForm, ExportForm,
    UnitEntryFormSet, WeightEntryFormSet,
)
from .models import (
    ConsumptionForm, ConsumptionProduct, WeightConsumptionProduct,
)


def dcf(request, pk):
    # Get event and verify rights
    event = get_object_or_404(Event, pk=pk)

    if not event.is_tender(request.user) and \
            not (request.organization.assigns_tenders and request.user.profile.is_tender(request.organization)):
        raise PermissionDenied(_('You are not a tender for this event.'))

    # Get consumption form or create one
    cf = event.consumptionform if hasattr(event, 'consumptionform') else ConsumptionForm(event=event)

    if cf.is_completed(request.user) \
            and not request.user.is_superuser \
            and not request.user.profile.is_foundation_manager:
        raise PermissionDenied(_('This consumption form has been completed.'))

    # Post or show form?
    if request.method == 'POST':
        form = ConsumptionFormForm(request.POST, instance=cf)
        weight_form = WeightEntryFormSet(request.POST, instance=cf)
        unit_form = UnitEntryFormSet(request.POST, instance=cf)
        if form.is_valid() and weight_form.is_valid() and unit_form.is_valid():
            form.save()
            weight_form.save()
            unit_form.save()
            return redirect('dcf', event.pk)
    else:
        form = ConsumptionFormForm(instance=cf)
        weight_form = WeightEntryFormSet(instance=cf)
        unit_form = UnitEntryFormSet(instance=cf)

    return render(request, 'consumption/dcf.html', locals())


def complete_dcf(request, pk):
    # Get event and verify rights
    event = get_object_or_404(Event, pk=pk)

    if not event.is_tender(request.user) and \
            not (request.organization.assigns_tenders and request.user.profile.is_tender(request.organization)):
        raise PermissionDenied(_('You are not a tender for this event'))

    if not hasattr(event, 'consumptionform'):
        raise Http404

    cf = event.consumptionform
    if cf.is_completed(request.user) \
            and not request.user.is_superuser \
            and not request.user.profile.is_foundation_manager:
        raise PermissionDenied(_('This consumption form has been completed.'))

    if request.method == 'POST':
        form = ConsumptionFormConfirmationForm(request.POST)
        if form.is_valid() and cf.is_valid():
            cf.completed_by = request.user
            cf.completed_at = timezone.now()
            cf.save()
            return render(request, 'consumption/dcf_finished.html', locals())
    else:
        form = ConsumptionFormConfirmationForm()

    return render(request, 'consumption/dcf_check.html', locals())


class ConsumptionFormExportView(FoundationManagerRequiredMixin, FormView):
    form_class = ExportForm
    template_name = 'consumption/dcf_export.html'

    def form_valid(self, form):
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        last_day = calendar.monthrange(year, month)[1]
        from_time = datetime.datetime(year, month, 1, tzinfo=timezone.utc)
        till_time = datetime.datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
        objects = ConsumptionForm.objects.filter(
            event__starts_at__gte=from_time,
            event__starts_at__lte=till_time,
        )
        filename = 'borrels-%s%d.%s' % (from_time.strftime('%B'), year, form.cleaned_data['format'])

        if form.cleaned_data['format'] == 'pdf':
            return self.pdf(filename, objects)
        elif form.cleaned_data['format'] == 'json':
            return self.json(filename, objects)

    def pdf(self, filename, objects):
        return PDFTemplateResponse(
            self.request,
            'consumption/dcf_pdf.html',
            context={'objects': objects},
            filename=filename,
        )

    def json(self, filename, objects):
        result = {}

        result['drinks'] = {}
        for organization in Organization.objects.all():
            forms = []
            for form in objects.filter(event__organizer=organization):
                if not form.is_completed():
                    continue
                forms.append({
                    'drink_name': form.event.name,
                    'date': form.event.starts_at.strftime('%d-%m-%Y'),
                    'products': form.aggregate_products(),
                    'location': [l.name for l in form.event.location.all()],
                })
            if forms:
                result['drinks'][organization.name] = forms

        result['products'] = {}
        for product in ConsumptionProduct.objects.all():
            result['products'][product.pk] = product.name

        response = JsonResponse(result, json_dumps_params={'indent': True})
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response


class ConsumptionProductListView(FoundationManagerRequiredMixin, ListView):
    queryset = ConsumptionProduct.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super(ConsumptionProductListView, self).get_context_data(**kwargs)
        context['archived_list'] = ConsumptionProduct.objects.filter(is_active=False)
        return context


class ConsumptionProductCreateView(FoundationManagerRequiredMixin, CrispyFormMixin, CreateView):
    model = ConsumptionProduct
    fields = ['name']
    success_url = reverse_lazy('consumptionproduct_list')
    template_name = 'consumption/consumptionproduct_form.html'


class WeightConsumptionProductCreateView(ConsumptionProductCreateView):
    model = WeightConsumptionProduct
    fields = ['name', 'full_weight', 'empty_weight', 'has_flowmeter']


class ConsumptionProductUpdateView(FoundationManagerRequiredMixin, CrispyFormMixin, UpdateView):
    model = ConsumptionProduct
    fields = ['name', 'is_active']
    success_url = reverse_lazy('consumptionproduct_list')
    template_name = 'consumption/consumptionproduct_form.html'


class WeightConsumptionProductUpdateView(ConsumptionProductUpdateView):
    model = WeightConsumptionProduct
    fields = ['name', 'full_weight', 'empty_weight', 'has_flowmeter', 'is_active']


class ConsumptionFormListView(ListView):
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super(ConsumptionFormListView, self).get_context_data(**kwargs)
        context['missing_dcf_list'] = Event.objects.filter(
            ends_at__lte=timezone.now(),
            ends_at__gte=timezone.now() - datetime.timedelta(days=30),
            consumptionform__isnull=True,
            kegs__gt=0,
        ).order_by('-starts_at').select_related('organizer')
        return context

    def get_queryset(self):
        if hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
        else:
            raise PermissionDenied

        if self.request.user.is_superuser or profile.is_foundation_manager:
            qs = ConsumptionForm.objects.all()
        elif profile.is_manager(self.request.organization):
            qs = ConsumptionForm.objects.filter(event__organizer=self.request.organization)
        else:
            raise PermissionDenied

        return qs \
            .order_by('-event__starts_at') \
            .prefetch_related('event__location') \
            .select_related('event__organizer')


class ConsumptionFormDetailView(DetailView):
    queryset = ConsumptionForm.objects.prefetch_related(
        'weightentry_set__product',
        'unitentry_set__product',
    ).select_related('completed_by', 'event')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.profile.is_foundation_manager \
                and not request.user.profile.is_manager(self.object.event.organizer):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ConsumptionFormPDFView(PDFTemplateView):
    template_name = 'consumption/dcf_pdf.html'

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(ConsumptionForm, pk=kwargs['pk'])

        if not request.user.profile.is_foundation_manager \
                and not request.user.profile.is_manager(self.object.event.organizer):
            raise PermissionDenied

        return super(ConsumptionFormPDFView, self).get(request, *args, **kwargs)

    def get_filename(self):
        return 'Verbruiksformulier %s.pdf' % self.object.event

    def get_context_data(self, **kwargs):
        context = super(ConsumptionFormPDFView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context
