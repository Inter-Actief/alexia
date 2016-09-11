from jsonrpc import jsonrpc_method

from apps.organization.models import Organization
from .common import api_v1_site
from .exceptions import NotFoundError


@jsonrpc_method('organization.current.get() -> String', site=api_v1_site, safe=True, authenticated=True)
def organization_current_get(request):
    """
    Return the current organization slug.

    Required user level: None

    All operations performed will be performed by this organization.

    If no organization has been chosen, it will return None.

    Example return value:
    "inter-actief"
    """

    if request.organization:
        return str(request.organization.slug)
    else:
        return None


@jsonrpc_method('organization.current.set(organization=String) -> Boolean', site=api_v1_site, authenticated=True)
def organization_current_set(request, organization):
    """
    Set the current organization.

    Required user level: None

    All further operations performed will be performed by this organization.

    Return true if the organization is switched. Returns false if the current
    organization equals the provided organization.

    organization    -- slug of the organization or empty string to deselect organization.

    Raises error 404 if provided organization cannot be found.
    """

    if not organization:
        if 'organization_pk' in request.session:
            del request.session['organization_pk']
            return True
        else:
            return False
    else:
        try:
            organization_pk = Organization.objects.get(slug=organization).pk
        except Organization.DoesNotExist:
            raise NotFoundError('Organization not found.')

        if request.session.get('organization_pk', None) != organization_pk:
            request.session['organization_pk'] = organization_pk
            return True
        else:
            return False


@jsonrpc_method('organization.list() -> Array', site=api_v1_site, safe=True, authenticated=True)
def organization_list(request):
    """
    List all public organizations.

    Required user level: None

    Returns a array with zero or more organizations.

    Exampel return value:
    [
        "abacus",
        "inter-actief",
        "proto",
        "scintilla",
        "sirius",
        "stress"
    ]
    """

    return [o.slug for o in Organization.public_objects.filter(is_public=True)]
