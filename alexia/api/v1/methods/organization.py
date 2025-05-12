from typing import Optional, List

from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import login_required
from alexia.api.exceptions import ObjectNotFoundError
from alexia.apps.organization.models import Organization


@rpc_method(name='organization.current.get', entry_point='v1')
@login_required
def organization_current_get(**kwargs) -> Optional[str]:
    """
    Return the current organization slug.

    Required user level: None

    All operations performed will be performed by this organization.

    If no organization has been chosen, it will return None.

    Example return value:
    "inter-actief"
    """
    request = kwargs.get(REQUEST_KEY)
    if request.organization:
        return request.organization.slug
    else:
        return None


@rpc_method(name='organization.current.set', entry_point='v1')
@login_required
def organization_current_set(organization: str, **kwargs) -> bool:
    """
    Set the current organization.

    Required user level: None

    All further operations performed will be performed by this organization.

    Return true if the organization is switched. Returns false if the current
    organization equals the provided organization.

    organization    -- slug of the organization or empty string to deselect organization.

    Raises error 404 if provided organization cannot be found.
    """
    request = kwargs.get(REQUEST_KEY)
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
            raise ObjectNotFoundError('Organization not found.')

        if request.session.get('organization_pk', None) != organization_pk:
            request.session['organization_pk'] = organization_pk
            return True
        else:
            return False


@rpc_method(name='organization.list', entry_point='v1')
@login_required
def organization_list(**kwargs) -> List[str]:
    """
    List all public organizations.

    Required user level: None

    Returns an array with zero or more organizations.

    Example return value:
    [
        "abacus",
        "inter-actief",
        "proto",
        "scintilla",
        "sirius",
        "stress"
    ]
    """
    return [o.slug for o in Organization.objects.all()]
