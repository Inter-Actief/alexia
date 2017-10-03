import mimetypes
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import (
    CreateView, DeleteView, FormView, ModelFormMixin, UpdateView,
)
from django.views.generic.list import ListView

from alexia.auth.backends import RADIUS_BACKEND_NAME
from alexia.auth.mixins import DenyWrongOrganizationMixin, ManagerRequiredMixin
from alexia.forms import CrispyFormMixin
from alexia.utils import log

from .forms import MembershipAddForm, UploadIvaForm
from .models import AuthenticationData, Membership, Profile


class MembershipListView(ManagerRequiredMixin, ListView):
    def get_queryset(self):
        return self.request.organization.membership_set.select_related(
                'user',
                'user__certificate',
                'user__certificate__approved_by',
                'user__profile',
            ).order_by('user__first_name')


class IvaListView(ManagerRequiredMixin, ListView):
    template_name_suffix = '_iva'

    def get_queryset(self):
        return self.request.organization.membership_set.filter(is_tender=True) \
            .select_related('user', 'user__certificate', 'user__profile').order_by('user__first_name')


class MembershipCreateView(ManagerRequiredMixin, CrispyFormMixin, FormView):
    form_class = MembershipAddForm
    template_name = 'organization/membership_form.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        try:
            authentication_data = AuthenticationData.objects.get(username=username, backend=RADIUS_BACKEND_NAME)
        except AuthenticationData.DoesNotExist:
            return redirect('add-membership', username=username)
        user = authentication_data.user
        membership, is_new = Membership.objects.get_or_create(user=user, organization=self.request.organization)
        if is_new:
            log.membership_created(self.request.user, membership)
        return redirect('edit-membership', pk=membership.pk)


class UserCreateView(ManagerRequiredMixin, CrispyFormMixin, CreateView):
    model = get_user_model()
    fields = ['first_name', 'last_name', 'email']

    def get_context_data(self, **kwargs):
        if AuthenticationData.objects.filter(username=self.kwargs['username'], backend=RADIUS_BACKEND_NAME).count():
            raise Http404('Account already exists')

        context = super(UserCreateView, self).get_context_data(**kwargs)
        context['username'] = self.kwargs['username']
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = self.kwargs['username']
        user.set_unusable_password()
        user.save()

        data = AuthenticationData(user=user, backend=RADIUS_BACKEND_NAME, username=self.kwargs['username'])
        data.save()

        profile = Profile(user=user)
        profile.save()

        membership, is_new = Membership.objects.get_or_create(user=user, organization=self.request.organization)
        if is_new:
            log.membership_created(self.request.user, membership)
        return redirect('edit-membership', pk=membership.pk)


class MembershipDetailView(ManagerRequiredMixin, DenyWrongOrganizationMixin, DetailView):
    model = Membership

    def get_context_data(self, **kwargs):
        context = super(MembershipDetailView, self).get_context_data(**kwargs)
        context.update({
            'last_10_tended': self.object.tended()[:10],
            'is_planner': self.request.user.is_superuser
            or self.request.user.profile.is_planner(self.request.organization),
        })
        context.update(self.get_graph_data())
        return context

    def get_graph_data(self):
        _last_year = (date.today()-relativedelta(years=1, day=1))
        _tended_dates = self.object.tended().filter(event__starts_at__gte=_last_year).values_list('event__starts_at')

        # Change from list of 1-tuples to just a list of elements
        _tended_dates = [i[0] for i in _tended_dates]

        # Group by month
        _graph_data = {}
        for d in _tended_dates:
            if d.strftime("%Y-%m") in _graph_data.keys():
                _graph_data[d.strftime("%Y-%m")] += 1
            else:
                _graph_data[d.strftime("%Y-%m")] = 1

        # Fill in 0 for the missing months
        _date = date.today()
        while _last_year <= _date:
            if _date.strftime("%Y-%m") not in _graph_data.keys():
                _graph_data[_date.strftime("%Y-%m")] = 0
            _date -= relativedelta(months=1)

        graph_headers = sorted(_graph_data.keys())
        return {
            'graph_headers': graph_headers,
            'graph_content': [_graph_data[k] for k in graph_headers],
        }


class MembershipUpdate(ManagerRequiredMixin, DenyWrongOrganizationMixin, CrispyFormMixin, UpdateView):
    model = Membership
    fields = ['is_active', 'is_tender', 'is_planner', 'is_manager', 'comments']


class MembershipDelete(ManagerRequiredMixin, DenyWrongOrganizationMixin, DeleteView):
    model = Membership
    success_url = reverse_lazy('memberships')


class MembershipIvaView(ManagerRequiredMixin, DenyWrongOrganizationMixin, DetailView):
    model = Membership

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        iva_file = self.object.user.certificate.file
        content_type, encoding = mimetypes.guess_type(iva_file.url)
        content_type = content_type or 'application/octet-stream'
        return HttpResponse(iva_file, content_type=content_type)


class MembershipIvaUpdate(ManagerRequiredMixin, DenyWrongOrganizationMixin, CrispyFormMixin, ModelFormMixin,
                          DetailView):
    model = Membership
    form_class = UploadIvaForm
    template_name = 'organization/certificate_form.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(MembershipIvaUpdate, self).get_form_kwargs()
        kwargs['instance'] = getattr(self.object.user, 'certificate', None)
        return kwargs

    def form_valid(self, form):
        if hasattr(self.object.user, 'certificate'):
            self.object.user.certificate.delete()
        certificate = form.save(commit=False)
        certificate.owner = self.object.user
        certificate.save()
        return redirect('memberships')


class MembershipIvaApprove(ManagerRequiredMixin, DenyWrongOrganizationMixin, SingleObjectMixin, RedirectView):
    model = Membership

    def get_redirect_url(self, *args, **kwargs):
        certificate = self.get_object().user.certificate
        if certificate and not certificate.approved_at:
            certificate.approve(self.request.user)
        return reverse('memberships')


class MembershipIvaDecline(ManagerRequiredMixin, DenyWrongOrganizationMixin, SingleObjectMixin, RedirectView):
    model = Membership

    def get_redirect_url(self, *args, **kwargs):
        certificate = self.get_object().user.certificate
        if certificate and not certificate.approved_at:
            certificate.decline()
        return reverse('memberships')
