from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import UpdateView
from djangosaml2.views import AssertionConsumerServiceView
from saml2.response import UnsolicitedResponse
from django.utils.translation import ugettext_lazy as _

from alexia.apps.organization.models import Location, Membership, Organization
from alexia.apps.scheduling.models import (
    Availability, BartenderAvailability, Event,
)

# Use this once LoginView is available in Django
#
# class LoginView(LoginView):
#     def form_valid(self, form):
#         user = form.get_user()
#         auth_login(self.request, user)
#
#         if hasattr(user, 'profile') and user.profile.current_organization:
#             self.request.session['organization_pk'] = user.profile.current_organization.pk
#
#         if not user.first_name or not user.email:
#             return HttpResponseRedirect(resolve_url('register'))
#
#         return HttpResponseRedirect(self.get_success_url())


def _get_login_redirect_url(request, redirect_to):
    # Ensure the user-originating redirection URL is safe.
    if not is_safe_url(url=redirect_to, allowed_hosts=request.get_host()):
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    return redirect_to

@login_required()
def login_complete(request):
    # After login, check if the user's profile is complete.
    # If it is not, send them to the page to complete the profile, else, send them to the main page.
    if not request.user.first_name or not request.user.email:
        return HttpResponseRedirect(resolve_url('register'))
    return HttpResponseRedirect("/")


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None, redirect_authenticated_user=False):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name, ''))

    if redirect_authenticated_user and request.user.is_authenticated:
        redirect_to = _get_login_redirect_url(request, redirect_to)
        if redirect_to == request.path:
            raise ValueError(
                "Redirection loop for authenticated user detected. Check that "
                "your LOGIN_REDIRECT_URL doesn't point to a login page."
            )
        return HttpResponseRedirect(redirect_to)
    elif request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            if hasattr(user, 'profile') and user.profile.current_organization:
                request.session['organization_pk'] = user.profile.current_organization.pk

            if not user.first_name or not user.email:
                return HttpResponseRedirect(resolve_url('register'))

            return HttpResponseRedirect(_get_login_redirect_url(request, redirect_to))
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


# The SAML login page throws a very annoying error when a timed-out response arrives,
# so we need to wrap it and ignore the error to stop it from showing up in our Sentry logs.
# Also, we need to inject the current onrganisation right after login.
class SAMLACSOverrideView(AssertionConsumerServiceView):
    @method_decorator(csrf_exempt)
    def post(self, *args, **kwargs):
        try:
            res = super(SAMLACSOverrideView, self).post(*args, **kwargs)
            if request.user:
                # Set current organisation
                if hasattr(request.user, 'profile') and request.user.profile.current_organization:
                    request.session['organization_pk'] = request.user.profile.current_organization.pk
            return res
        except UnsolicitedResponse:
            raise PermissionDenied(_("Logging in failed, please try again."))


class RegisterView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/register.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('event-list')

    def get_object(self):
        return self.request.user


class ChangeCurrentOrganizationView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        organization = get_object_or_404(Organization, slug=kwargs['slug'])
        self.request.session['organization_pk'] = organization.pk
        self.request.user.profile.current_organization = organization
        self.request.user.profile.save()
        return self.request.POST.get(REDIRECT_FIELD_NAME, self.request.GET.get(REDIRECT_FIELD_NAME, ''))


class AboutView(TemplateView):
    template_name = 'general/about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['count'] = {
            'organizations': Organization.objects.count(),
            'users': get_user_model().objects.count(),
            'tenders': Membership.objects.values('user_id').distinct().count(),
            'locations': Location.objects.count(),
            'first_event': Event.objects.order_by('starts_at')[0],
            'events': Event.objects.count(),
            'bartender_availabilities': BartenderAvailability.objects.count(),
            'bartender_availabilities_yes': BartenderAvailability.objects.filter(
                availability__nature__in=(Availability.ASSIGNED, Availability.YES),
            ).count(),
            'bartender_availabilities_assigned': BartenderAvailability.objects.filter(
                availability__nature=Availability.ASSIGNED,
            ).count(),
        }
        return context


class HelpView(TemplateView):
    template_name = 'general/help.html'
