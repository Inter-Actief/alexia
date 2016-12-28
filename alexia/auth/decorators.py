from functools import wraps

from django.core.exceptions import PermissionDenied


def manager_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_manager(request.organization)):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrap
