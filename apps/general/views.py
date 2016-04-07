from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, resolve_url, get_object_or_404
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_protect

from apps.organization.models import Organization, Location, Membership
from apps.scheduling.models import Event, BartenderAvailability, Availability
from .forms import RegisterForm


@csrf_protect
def login(request):
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, ''))

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Worden we wel naar een veilige pagina gestuurd?
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            user = form.get_user()
            auth_login(request, user)

            # Primaire organisatie instellen
            if hasattr(user, 'profile') and user.profile.current_organization:
                request.session['organization_pk'] = user.profile.current_organization.pk

            if not user.first_name or not user.email:
                # User information is not complete, redirect to register page.
                return redirect(register)

            return redirect(redirect_to)
    else:
        form = AuthenticationForm(request)

    redirect_field_name = REDIRECT_FIELD_NAME

    return render(request, 'general/login.html', locals())


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)


@login_required
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('apps.scheduling.views.overview')
    else:
        form = RegisterForm(instance=request.user)

    return render(request, 'general/register.html', locals())


@login_required
def change_current_organization(request, organization):
    org = get_object_or_404(Organization, slug=organization)
    request.session['organization_pk'] = org.pk
    request.user.profile.current_organization = org
    request.user.profile.save()
    return redirect(request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, '')))


def about(request):
    count = {
        'organizations': Organization.objects.count(),
        'users': User.objects.count(),
        'tenders': Membership.objects.values('user_id').distinct().count(),
        'locations': Location.objects.count(),
        'public_locations': Location.objects.filter(is_public=True).count(),
        'first_event': Event.objects.order_by('starts_at')[0],
        'events': Event.objects.count(),
        'bartender_availabilities': BartenderAvailability.objects.count(),
        'bartender_availabilities_yes': BartenderAvailability.objects.filter(
            availability__nature__in=(Availability.ASSIGNED, Availability.YES)).count(),
        'bartender_availabilities_assigned': BartenderAvailability.objects.filter(
            availability__nature=Availability.ASSIGNED).count(),
    }
    return render(request, 'general/about.html', locals())


def help(request):
    return render(request, 'general/help.html')
