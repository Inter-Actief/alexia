import mimetypes
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from alexia.apps.billing.models import Order
from alexia.apps.organization.models import AuthenticationData, Certificate
from alexia.apps.scheduling.models import Event
from alexia.auth.backends import RADIUS_BACKEND_NAME
from alexia.auth.mixins import TenderRequiredMixin
from alexia.forms import AlexiaModelForm, CrispyFormMixin


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({
            'events': Event.objects.filter(orders__authorization__in=self.request.user.authorizations.all())
                                   .annotate(spent=Sum('orders__amount'))
                                   .order_by('ends_at'),
            'order_count': Order.objects.select_related('event')
                                        .filter(authorization__in=self.request.user.authorizations.all())
                                        .count(),
            'shares': self.get_shares(self.request.user),
            'radius_username': self.get_radius_username(self.request.user),
        })
        return context

    def get_shares(self, user):
        shares = []

        for authorization in user.authorizations.all():
            my_order_sum = Order.objects.filter(authorization=authorization).aggregate(total=Sum('amount'))
            all_order_sum = Order.objects.filter(authorization__organization=authorization.organization) \
                .aggregate(total=Sum('amount'))

            if not my_order_sum['total'] or not all_order_sum['total']:
                percentage = 0
            else:
                percentage = (my_order_sum['total'] / all_order_sum['total']) * 100

            shares.append({'organization': authorization.organization, 'percentage': round(percentage, 2)})

        return shares

    def get_radius_username(self, user):
        try:
            return self.request.user.authenticationdata_set.get(backend=RADIUS_BACKEND_NAME).username
        except AuthenticationData.DoesNotExist:
            return None


class GenerateIcalView(TenderRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.request.user.profile.ical_id = uuid.uuid4()
        self.request.user.profile.save()
        return reverse('profile')


class ProfileUpdate(LoginRequiredMixin, CrispyFormMixin, UpdateView):
    template_name = 'profile_form.html'
    fields = ['email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')


class IvaForm(AlexiaModelForm):
    class Meta:
        model = Certificate
        fields = ['file']


@login_required
def iva(request):
    certificate = getattr(request.user, 'certificate', None)

    if request.method == 'POST':
        form = IvaForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete the old
            if certificate:
                certificate.delete()
            # Save the new
            certificate = form.save(commit=False)
            certificate._id = str(request.user.pk)
            certificate.save()
            # Attach to profile
            request.user.certificate = certificate
            request.user.save()

            return redirect('profile')
    else:
        form = IvaForm(instance=certificate)

    return render(request, 'profile/iva.html', locals())


class IvaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not request.user.certificate:
            raise Http404

        iva_file = request.user.certificate.file
        content_type, encoding = mimetypes.guess_type(iva_file.url)
        content_type = content_type or 'application/octet-stream'
        return HttpResponse(iva_file, content_type=content_type)


class ExpenditureListView(LoginRequiredMixin, ListView):
    template_name = 'billing/expenditure_list.html'
    paginate_by = 25

    def get_queryset(self):
        return Event.objects.filter(orders__authorization__in=self.request.user.authorizations.all()) \
                            .annotate(spent=Sum('orders__amount')) \
                            .order_by('-ends_at')


class ExpenditureDetailView(LoginRequiredMixin, DetailView):
    template_name = 'billing/expenditure_detail.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(ExpenditureDetailView, self).get_context_data(**kwargs)
        context['order_list'] = self.object.orders.filter(authorization__in=self.request.user.authorizations.all()) \
                                                  .order_by('-placed_at')
        return context
