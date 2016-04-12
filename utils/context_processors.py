from apps.organization.models import Organization


def organization(request):
    """Provides the primary organization to the template."""
    return {
        'current_organization': request.organization,
        'organizations': Organization.public_objects.all()
    }
