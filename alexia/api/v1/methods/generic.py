from django.db import transaction
from jsonrpc import jsonrpc_method

from ..config import api_v1_site


@jsonrpc_method('version() -> Number', site=api_v1_site, safe=True)
def version(request):
    """
    Returns the current API version.

    Required user level: None

    The client will then be able to determine which methods it can use and
    which methods it cannot use.

    A client can expect to have no issues if the client uses the same API
    version. In other cases, this API does not guarantee anything.
    """
    return 1


@jsonrpc_method('methods() -> Array', site=api_v1_site, safe=True)
def methods(request):
    """
    Introspect the API and return all callable methods.

    Required user level: None

    Returns an array with the methods.
    """
    result = []

    for proc in api_v1_site.describe(request)['procs']:
        result.append(proc['name'])

    return result


@jsonrpc_method('login(username=String, password=String) -> Boolean', site=api_v1_site)
@transaction.atomic
def login(request, username, password):
    """
    Authenticate an user to use the API.

    Required user level: None

    Returns true when an user has successful signed in. A session will be
    started and stored. Cookies must be supported by the client.

    username        -- Username of user
    password        -- Password of the user
    """
    from django.contrib.auth import authenticate, login

    user = authenticate(username=username, password=password)

    if user is None or user.is_active is False:
        return False
    else:
        login(request, user)
        return True


@jsonrpc_method('logout() -> Nil', site=api_v1_site)
@transaction.atomic
def logout(request):
    """
    Sign out the current user, even if no one was signed in.

    Required user level: None

    Destroys the current session.
    """
    from django.contrib.auth import logout

    logout(request)
