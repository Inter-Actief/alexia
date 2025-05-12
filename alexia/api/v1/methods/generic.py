from typing import List

from django.db import transaction
from modernrpc.core import rpc_method, registry, REQUEST_KEY, ENTRY_POINT_KEY, PROTOCOL_KEY


@rpc_method(name='version', entry_point='v1')
def version(**kwargs) -> int:
    """
    **Signature**: `version()`

    **Arguments**:

    - *None*

    **Return type**: `int`

    **Idempotent**: yes

    **Required user level**: *None*

    **Documentation**:

    Returns the current API version.

    The client will then be able to determine which methods it can use and
    which methods it cannot use.

    A client can expect to have no issues if the client uses the same API
    version. In other cases, this API does not guarantee anything.
    """
    return 1


@rpc_method(name='methods', entry_point='v1')
def methods(**kwargs) -> List[str]:
    """
    **Signature**: `methods()`

    **Arguments**:

    - *None*

    **Return type**: List of `str`

    **Idempotent**: yes

    **Required user level**: Manager

    **Documentation**:

    Introspect the API and return all callable methods.

    Returns an array with the methods.
    """
    entry_point = kwargs.get(ENTRY_POINT_KEY)
    protocol = kwargs.get(PROTOCOL_KEY)

    return registry.get_all_method_names(entry_point, protocol, sort_methods=True)


@rpc_method(name='login', entry_point='v1')
@transaction.atomic
def login(username: str, password: str, **kwargs) -> bool:
    """
    **Signature**: `login()`

    **Arguments**:

    - `username` : `str` -- Username of user.
    - `password` : `str` -- Password of the user.

    **Return type**: `bool`

    **Idempotent**: no

    **Required user level**: *None*

    **Documentation**:

    Authenticate a user to use the API.

    Returns `True` when a user has successfully signed in. A session will be
    started and stored. Cookies must be supported by the client.
    """
    from django.contrib.auth import authenticate, login
    request = kwargs.get(REQUEST_KEY)

    # TODO: Authenticating for the API will be hard once RADIUS shuts down. As a stopgap, we can give each association
    #       a local Alexia account to use for the API, but in due time we will probably want to move to something
    #       better like an oAuth based API... - albertskja, 19-09-2019
    user = authenticate(username=username, password=password)

    if user is None or user.is_active is False:
        return False
    else:
        login(request, user)
        return True


@rpc_method(name='logout', entry_point='v1')
@transaction.atomic
def logout(**kwargs) -> None:
    """
    **Signature**: `logout()`

    **Arguments**:

    - *None*

    **Return type**: `None`

    **Idempotent**: no

    **Required user level**: *None*

    **Documentation**:

    Sign out the current user, even if no one was signed in.

    Destroys the current session.
    """
    from django.contrib.auth import logout
    request = kwargs.get(REQUEST_KEY)

    logout(request)
