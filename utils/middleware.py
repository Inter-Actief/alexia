from django.utils.deprecation import MiddlewareMixin

from apps.organization.models import Organization, Profile


def profile_requirement_middleware(get_response):

    def middleware(request):
        if request.user.is_authenticated() and not Profile.objects.filter(user=request.user).exists():
            Profile(user=request.user).save()
        return get_response(request)

    return middleware


def primary_organization_middleware(get_response):
    
    def middleware(request):
        if 'organization_pk' in request.session:
            request.organization = Organization.objects.get(pk=request.session['organization_pk'])
        else:
            request.organization = None

        return get_response(request)

    return middleware
