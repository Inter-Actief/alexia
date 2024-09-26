from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear, TruncMonth
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.dates import MONTHS
from django.utils.translation import ugettext as _
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import (
    CreateView, DeleteView, FormMixin, FormView, UpdateView,
)
from django.views.generic.list import ListView

from alexia.apps.billing.forms import (
    DeletePriceGroupForm, FilterEventForm, PermanentProductForm,
    SellingPriceForm,
)
from alexia.apps.billing.models import (
    PermanentProduct, PriceGroup, Product, ProductGroup, SellingPrice,
    TemporaryProduct,
)
from alexia.apps.scheduling.models import Event
from alexia.auth.mixins import (
    DenyWrongOrganizationMixin, ManagerRequiredMixin, TenderRequiredMixin,
)
from alexia.forms import CrispyFormMixin
from alexia.views import (
    CreateViewForOrganization, EventOrganizerFilterMixin, FixedValueCreateView,
    OrganizationFilterMixin, OrganizationFormMixin,
)

from .models import Order, Purchase, WriteoffCategory


class JulianaView(TenderRequiredMixin, DetailView):
    template_name = 'billing/juliana.html'
    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.is_tender(request.user):
            raise PermissionDenied(_('You are not a tender for this event'))
        if not self.object.can_be_opened(request.user):
            raise PermissionDenied(_('This event is not open'))

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JulianaView, self).get_context_data(**kwargs)
        context.update({
            'products': self.get_product_list(),
            'countdown': settings.JULIANA_COUNTDOWN if hasattr(settings, 'JULIANA_COUNTDOWN') else 5,
            'androidapp': self.request.META.get('HTTP_X_REQUESTED_WITH') == 'net.inter_actief.juliananfc',
            'writeoff': self.object.organizer.writeoff_enabled,
            'writeoff_categories' : WriteoffCategory.objects.filter(organization=self.object.organizer, is_active=True)
        })
        return context

    def get_product_list(self):
        products = []

        for sellingprice in self.object.pricegroup.sellingprice_set.all():
            for product in sellingprice.productgroup.permanentproduct_set.all():
                products.append({
                    'id': product.pk,
                    'name': product.name,
                    'shortcut': product.shortcut.upper(),
                    'text_color': product.text_color,
                    'background_color': product.background_color,
                    'price': int(sellingprice.price * 100),
                    'position': product.position,
                })

        products.sort(key=lambda x: x['position'])

        for product in self.object.temporaryproducts.all():
            products.append({
                'id': product.pk,
                'name': product.name,
                'shortcut': product.shortcut.upper(),
                'text_color': product.text_color,
                'background_color': product.background_color,
                'price': int(product.price * 100),
            })

        return products


class OrderListView(ManagerRequiredMixin, ListView):
    template_name = 'billing/order_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.organization) \
            .annotate(
                order_count=Count('orders'),
                revenue=Sum('orders__amount'),
                visitors=Count('orders__authorization', distinct=True),
            ) \
            .filter(order_count__gt=0, ) \
            .order_by('-starts_at') \
            .select_related('pricegroup')

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['stats_years'] = Event.objects \
            .filter(organizer=self.request.organization) \
            .annotate(year=ExtractYear('starts_at')) \
            .values('year') \
            .order_by('-year') \
            .annotate(revenue=Sum('orders__amount'))[:3]
        return context


class OrderDetailView(ManagerRequiredMixin, DenyWrongOrganizationMixin, DetailView):
    model = Event
    template_name = 'billing/order_detail.html'
    organization_field = 'organizer'

    def get_context_data(self, **kwargs):
        products = Purchase.objects.filter(order__event=self.object) \
            .values('product') \
            .annotate(amount=Sum('amount'), price=Sum('price'))

        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context.update({
            'orders': self.object.orders.select_related('authorization__user').order_by('-placed_at'),
            'products': products,
            'revenue': products.aggregate(Sum('price'))['price__sum'],
        })
        return context


class OrderExportView(ManagerRequiredMixin, FormView):
    template_name = 'billing/order_export_form.html'
    form_class = FilterEventForm

    def form_valid(self, form):
        event_list = Event.objects.filter(
            organizer=self.request.organization,
            starts_at__gte=form.cleaned_data['from_time'],
            starts_at__lte=form.cleaned_data['till_time'],
        )
        events = event_list \
            .annotate(order_count=Count('orders'), revenue=Sum('orders__amount')) \
            .filter(order_count__gt=0) \
            .order_by('starts_at')
        summary = event_list \
            .annotate(month=TruncMonth('starts_at')) \
            .values('month') \
            .annotate(revenue=Sum('orders__amount')) \
            .order_by('month')
        return render(self.request, 'billing/order_export_result.html', locals())


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'billing/payment_detail.html'

    def get_object(self, queryset=None):
        obj = super(PaymentDetailView, self).get_object(queryset)

        if not self.request.user.is_superuser \
                and not self.request.user.profile.is_manager(obj.authorization.organization) \
                and not obj.authorization.user == self.request.user:
            raise PermissionDenied

        return obj


class OrderYearView(ManagerRequiredMixin, TemplateView):
    template_name = 'billing/order_year.html'

    def get_context_data(self, **kwargs):
        context = super(OrderYearView, self).get_context_data(**kwargs)
        context['obj_list'] = Event.objects.filter(
            organizer=self.request.organization,
            starts_at__year=kwargs['year'],
        ).annotate(
            date=TruncMonth('starts_at'),
        ).values('date').annotate(
            revenue=Sum('orders__amount'),
        ).order_by('date')
        return context


class OrderMonthView(ManagerRequiredMixin, TemplateView):
    template_name = 'billing/order_month.html'

    def get_context_data(self, **kwargs):
        if int(kwargs['month']) not in range(1, 13):
            raise Http404

        context = super(OrderMonthView, self).get_context_data(**kwargs)
        context['event_list'] = Event.objects.filter(
            organizer=self.request.organization,
            starts_at__year=kwargs['year'],
            starts_at__month=kwargs['month'],
        ).annotate(revenue=Sum('orders__amount')).order_by('starts_at')
        context['month_name'] = MONTHS[int(kwargs['month'])]
        return context


class PriceGroupListView(ManagerRequiredMixin, OrganizationFilterMixin, ListView):
    model = PriceGroup


class PriceGroupDetailView(ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    model = PriceGroup


class PriceGroupCreateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin, CreateViewForOrganization):
    model = PriceGroup
    fields = ['name']


class PriceGroupUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin, UpdateView):
    model = PriceGroup
    fields = ['name']


class PriceGroupDeleteView(ManagerRequiredMixin, OrganizationFilterMixin, FormMixin, DeleteView):
    model = PriceGroup
    success_url = reverse_lazy('pricegroup_list')
    form_class = DeletePriceGroupForm

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            Event.objects.filter(pricegroup=self.object).update(pricegroup=form.cleaned_data['new_pricegroup'])
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(PriceGroupDeleteView, self).get_form_kwargs()
        kwargs['queryset'] = PriceGroup.objects.filter(organization=self.request.organization) \
            .exclude(pk=self.object.pk)
        return kwargs


class ProductGroupListView(ManagerRequiredMixin, OrganizationFilterMixin, ListView):
    model = ProductGroup


class ProductGroupDetailView(ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    model = ProductGroup


class ProductGroupCreateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin,
                             CreateViewForOrganization):
    model = ProductGroup
    fields = ['name']


class ProductGroupUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, CrispyFormMixin, UpdateView):
    model = ProductGroup
    fields = ['name']


class ProductGroupDeleteView(ManagerRequiredMixin, OrganizationFilterMixin, DeleteView):
    model = ProductGroup
    success_url = reverse_lazy('productgroup_list')


class ProductRedirectView(ManagerRequiredMixin, SingleObjectMixin, RedirectView):
    model = Product
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        obj = self.get_object()

        if obj.is_permanent:
            self.pattern_name = 'product_detail'
        elif obj.is_temporary:
            self.pattern_name = 'temporaryproduct_detail'
        else:
            raise ValueError('Product is neither permament nor temporary')

        return super(ProductRedirectView, self).get_redirect_url(*args, **kwargs)


class ProductListView(ManagerRequiredMixin, OrganizationFilterMixin, ListView):
    queryset = PermanentProduct.objects.select_related('productgroup')


class ProductDetailView(ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    model = PermanentProduct


class ProductCreateView(ManagerRequiredMixin, OrganizationFormMixin, CrispyFormMixin, CreateViewForOrganization):
    model = PermanentProduct
    form_class = PermanentProductForm

    def get_initial(self):
        initial = super(ProductCreateView, self).get_initial()
        if 'productgroup_pk' in self.kwargs:
            initial['productgroup'] = get_object_or_404(ProductGroup, pk=self.kwargs['productgroup_pk'])
        return initial


class ProductUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, OrganizationFormMixin, CrispyFormMixin,
                        UpdateView):
    model = PermanentProduct
    form_class = PermanentProductForm


class ProductDeleteView(ManagerRequiredMixin, OrganizationFilterMixin, DeleteView):
    model = PermanentProduct
    success_url = reverse_lazy('product_list')


class TemporaryProductCreateView(ManagerRequiredMixin, CrispyFormMixin, FixedValueCreateView):
    model = TemporaryProduct
    fields = ['name', 'price', 'text_color', 'background_color']

    def get_instance(self):
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        return self.model(event=event)

    def get_success_url(self):
        return reverse('event', args=[self.object.event.pk])


class TemporaryProductUpdateView(ManagerRequiredMixin, EventOrganizerFilterMixin, CrispyFormMixin, UpdateView):
    model = TemporaryProduct
    fields = ['name', 'price', 'text_color', 'background_color']

    def get_success_url(self):
        return reverse('event', args=[self.object.event.pk])


class TemporaryProductDeleteView(ManagerRequiredMixin, EventOrganizerFilterMixin, DeleteView):
    model = TemporaryProduct

    def get_success_url(self):
        return reverse('event', args=[self.object.event.pk])


class SellingPriceCreateView(ManagerRequiredMixin, OrganizationFormMixin, CrispyFormMixin, CreateView):
    model = SellingPrice
    form_class = SellingPriceForm

    def get_initial(self):
        initial = super(SellingPriceCreateView, self).get_initial()
        if 'pricegroup_pk' in self.kwargs:
            initial['pricegroup'] = get_object_or_404(PriceGroup, pk=self.kwargs['pricegroup_pk'])
        if 'productgroup_pk' in self.kwargs:
            initial['productgroup'] = get_object_or_404(ProductGroup, pk=self.kwargs['productgroup_pk'])
        return initial


class SellingPriceFilterMixin(object):
    def get_queryset(self):
        organization = self.request.organization
        return super(SellingPriceFilterMixin, self).get_queryset().filter(pricegroup__organization=organization,
                                                                          productgroup__organization=organization)


class SellingPriceUpdateView(ManagerRequiredMixin, SellingPriceFilterMixin, OrganizationFormMixin, CrispyFormMixin,
                             UpdateView):
    model = SellingPrice
    form_class = SellingPriceForm
    success_url = reverse_lazy('sellingprice_list')


class SellingPriceDeleteView(ManagerRequiredMixin, SellingPriceFilterMixin, DeleteView):
    model = SellingPrice

    def get_success_url(self):
        return self.object.pricegroup.get_absolute_url()


class SellingPriceListView(ManagerRequiredMixin, TemplateView):
    template_name = 'billing/sellingprice_list.html'

    def get_context_data(self, **kwargs):
        context = super(SellingPriceListView, self).get_context_data(**kwargs)

        organization = self.request.organization

        pricegroups = organization.pricegroups.prefetch_related('sellingprice_set', 'sellingprice_set__productgroup')
        productgroups = ProductGroup.objects.filter(organization=organization)

        pricedata = dict([(pricegroup,
                           dict([(sellingprice.productgroup, sellingprice)
                                 for sellingprice in pricegroup.sellingprice_set.all()]))
                          for pricegroup in pricegroups])
        """ Dict pricegroup -> productgroup -> sellingprice """

        data = []
        """ List of (productgroup, [(pricegroup, sellingprice), ...]) tuples """

        for productgroup in productgroups:
            data.append((productgroup,
                         [(pricegroup,
                           pricedata[pricegroup][productgroup] if productgroup in pricedata[pricegroup] else None)
                          for pricegroup in pricegroups]
                         ))

        context['pricegroups'] = pricegroups
        context['productgroups'] = data
        return context
