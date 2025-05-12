from typing import Optional, List

from modernrpc.core import rpc_method, REQUEST_KEY

from alexia.api.decorators import login_required
from alexia.api.exceptions import ObjectNotFoundError
from alexia.apps.organization.models import Organization


@rpc_method(name='organization.current.get', entry_point='v1')
@login_required
def organization_current_get(**kwargs) -> Optional[str]:
    """
    **Signature**: `organization.current.get()`

    **Arguments**:

    - *None*

    **Return type**: *(optional)* `str`

    **Idempotent**: yes

    **Required user level**: *None*

    **Documentation**:

    Return the current organization slug.

    All operations performed will be performed by this organization.

    If no organization has been chosen, it will return `None`.

    **Example return value**:

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
    **Signature**: `organization.current.set(organization)`

    **Arguments**:

    - `organization` : `str` -- slug of the organization or empty string to deselect organization.

    **Return type**: `bool`

    **Idempotent**: no

    **Required user level**: *None*

    **Documentation**:

    Set the current organization.

    All further operations performed will be performed by this organization.

    Return `True` if the organization is switched. Returns `False` if the current
    organization equals the provided organization.

    **Raises errors**:

    - `404` (Object not found) if provided organization cannot be found.
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
    **Signature**: `organization.list()`

    **Arguments**:

    - *None*

    **Return type**: List of `str`

    **Idempotent**: no

    **Required user level**: *None*

    **Documentation**:

    List all public organizations.

    Returns an array with zero or more organizations.

    **Example return value**:

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
