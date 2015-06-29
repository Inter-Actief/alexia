from apps.organization.models import Organization


def primary_organization(request):
    """Provides the primary organization to the template."""

    return {
        'current_organization': lambda: request.organization,
        'organizations': lambda: Organization.public_objects.all()
    }
