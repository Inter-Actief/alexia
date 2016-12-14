from alexia.apps.organization.models import Organization


def organization(request):
    return {
        'current_organization': request.organization,
        'organizations': Organization.public_objects.all()
    }
