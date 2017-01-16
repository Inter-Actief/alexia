from alexia.apps.organization.models import Organization, Profile


class CommonMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.ensure_profile(request)
        self.get_current_organization(request)
        return self.get_response(request)

    def ensure_profile(self, request):
        if request.user.is_authenticated() and not hasattr(request.user, 'profile'):
            Profile(user=request.user).save()

    def get_current_organization(self, request):
        request.organization = None
        if 'organization_pk' in request.session:
            request.organization = Organization.objects.get(pk=request.session['organization_pk'])
