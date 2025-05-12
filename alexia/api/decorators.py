from functools import wraps

from django.core.exceptions import PermissionDenied
from modernrpc.core import REQUEST_KEY


def manager_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        request = kwargs.get(REQUEST_KEY)
        if not request.user.is_authenticated or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_manager(request.organization)
        ):
            raise PermissionDenied
        return f(*args, **kwargs)
    return wrap

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        request = kwargs.get(REQUEST_KEY)
        if not request.user.is_authenticated:
            raise PermissionDenied
        return f(*args, **kwargs)
    return wrap
