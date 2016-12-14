from alexia.apps.organization.models import Organization, Profile


class CommonMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated() and not Profile.objects.filter(user=request.user).exists():
            Profile(user=request.user).save()

        if 'organization_pk' in request.session:
            request.organization = Organization.objects.get(pk=request.session['organization_pk'])
        else:
            request.organization = None

        return self.get_response(request)
