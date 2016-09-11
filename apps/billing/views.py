from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from apps.billing.forms import PermanentProductForm, SellingPriceForm
from apps.billing.models import (
    PermanentProduct, PriceGroup, Product, ProductGroup, SellingPrice,
    TemporaryProduct,
)
from apps.scheduling.models import Event
from utils.auth.decorators import manager_required
from utils.auth.mixins import ManagerRequiredMixin
from utils.mixins import (
    CreateViewForOrganization, CrispyFormMixin, EventOrganizerFilterMixin,
    FixedValueCreateView, OrganizationFilterMixin, OrganizationFormMixin,
)

from .models import Order, Purchase


@login_required
@manager_required
def order_list(request):
    event_list = Event.objects.filter(organizer=request.organization) \
        .annotate(order_count=Count('orders'), revenue=Sum('orders__amount')) \
        .filter(order_count__gt=0, ) \
        .order_by('-starts_at')
    paginator = Paginator(event_list, 20)

    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    year_sql = connection.ops.date_extract_sql('year', 'starts_at')
    stats_years = Event.objects.extra({'year': year_sql}) \
                       .filter(organizer=request.organization).values('year') \
                       .annotate(revenue=Sum('orders__amount')).order_by('-year')[:3]

    return render(request, "order/list.html", locals())


@login_required
@manager_required
def order_show(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.organization != event.organizer:
        raise PermissionDenied

    products = Purchase.objects.filter(order__event=event) \
        .values('product', 'product__name') \
        .annotate(amount=Sum('amount'), price=Sum('price'))

    orders = event.orders.select_related('authorization__user').order_by('-placed_at')
    order_count = len(orders)  # efficientie: len() ipv count()
    order_sum = orders.aggregate(Sum('amount'))['amount__sum']

    return render(request, "order/show.html", locals())


@login_required
def payment_show(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # bekijk als: * dit mijn transactie is
    #             * ik manager van de vereniging in kwestie ben
    #             * ik superuser ben
    if (order.authorization.user == request.user) \
            or request.user.is_superuser \
            or (request.organization and
                request.organization == order.authorization.organization and
                request.user.profile.is_manager(request.organization)):
        return render(request, 'payment/show.html', locals())

    raise PermissionDenied


@login_required
@manager_required
def stats_year(request, year):
    months = Event.objects.extra({'month': "month(starts_at)"}) \
        .filter(organizer=request.organization, starts_at__year=year) \
        .values('month').annotate(revenue=Sum('orders__amount')) \
        .order_by('month')
    return render(request, "order/stats_year.html", locals())


@login_required
@manager_required
def stats_month(request, year, month):
    month = int(month)
    events = Event.objects.filter(
        organizer=request.organization,
        starts_at__year=year,
        starts_at__month=month,
    ).annotate(revenue=Sum('orders__amount')).order_by('starts_at')

    return render(request, "order/stats_month.html", locals())


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


class ProductRedirectView(ManagerRequiredMixin, SingleObjectMixin, RedirectView):
    """
    View to redirect to either the PermanentProductDetailView or the
    TemporaryProductDetailView depending on the type of product.
    """
    model = Product
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        obj = self.get_object()

        if obj.is_permanent:
            self.pattern_name = 'permanentproduct_detail'
        elif obj.is_temporary:
            self.pattern_name = 'temporaryproduct_detail'
        else:
            raise ValueError('Product is neither permament nor temporary')

        return super(ProductRedirectView, self).get_redirect_url(*args, **kwargs)


class PermanentProductListView(ManagerRequiredMixin, OrganizationFilterMixin, ListView):
    model = PermanentProduct

    def get_queryset(self):
        return super(PermanentProductListView, self).get_queryset().order_by('position')


class PermanentProductDetailView(ManagerRequiredMixin, OrganizationFilterMixin, DetailView):
    model = PermanentProduct


class PermanentProductCreateView(ManagerRequiredMixin, OrganizationFormMixin, CrispyFormMixin,
                                 CreateViewForOrganization):
    """
    Create view for permanent products.

    Sets initial ProductGroup if productgroup_pk is provided.
    """

    model = PermanentProduct
    form_class = PermanentProductForm

    def get_initial(self):
        initial = super(PermanentProductCreateView, self).get_initial()
        if 'productgroup_pk' in self.kwargs:
            initial['productgroup'] = get_object_or_404(ProductGroup, pk=self.kwargs['productgroup_pk'])
        return initial


class PermanentProductUpdateView(ManagerRequiredMixin, OrganizationFilterMixin, OrganizationFormMixin, CrispyFormMixin,
                                 UpdateView):
    model = PermanentProduct
    form_class = PermanentProductForm


class TemporaryProductDetailView(ManagerRequiredMixin, EventOrganizerFilterMixin, DetailView):
    model = TemporaryProduct


class TemporaryProductCreateView(ManagerRequiredMixin, CrispyFormMixin, FixedValueCreateView):
    model = TemporaryProduct
    fields = ['name', 'price', 'text_color', 'background_color']

    def get_instance(self):
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        return self.model(event=event)


class TemporaryProductUpdateView(ManagerRequiredMixin, EventOrganizerFilterMixin, CrispyFormMixin, UpdateView):
    model = TemporaryProduct
    fields = ['name', 'price', 'text_color', 'background_color']


class SellingPriceCreateView(ManagerRequiredMixin, OrganizationFormMixin, CrispyFormMixin, CreateView):
    """
    Create view for selling prices.

    Sets initial PriceGroup or ProductGroup if pricegroup_pk or productgroup_pk is provided.
    """

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
    """
    Mixin to select only SellingPrice object belonging to the current organization.
    """

    def get_queryset(self):
        organization = self.request.organization
        return super(SellingPriceFilterMixin, self).get_queryset().filter(pricegroup__organization=organization,
                                                                          productgroup__organization=organization)


class SellingPriceUpdateView(ManagerRequiredMixin, SellingPriceFilterMixin, OrganizationFormMixin, CrispyFormMixin,
                             UpdateView):
    model = SellingPrice
    form_class = SellingPriceForm


class SellingPriceDeleteView(ManagerRequiredMixin, SellingPriceFilterMixin, DeleteView):
    model = SellingPrice

    def get_success_url(self):
        return self.object.pricegroup.get_absolute_url()


class SellingPriceMatrixView(ManagerRequiredMixin, TemplateView):
    """
    Price matrix view.

    Displays a matrix with all pricegroup-productgroup combinations.
    """
    template_name = 'billing/sellingprice_matrix.html'

    def get_context_data(self, **kwargs):
        context = super(SellingPriceMatrixView, self).get_context_data(**kwargs)

        organization = self.request.organization

        pricegroups = PriceGroup.objects.filter(organization=organization) \
            .prefetch_related('sellingprice_set', 'sellingprice_set__productgroup')
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
