from django.utils.deprecation import MiddlewareMixin

from apps.organization.models import Organization, Profile


class ProfileRequirementMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated() and not Profile.objects.filter(user=request.user).exists():
            Profile(user=request.user).save()


class PrimaryOrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'organization_pk' in request.session:
            request.organization = Organization.objects.get(pk=request.session['organization_pk'])
        else:
            request.organization = None
