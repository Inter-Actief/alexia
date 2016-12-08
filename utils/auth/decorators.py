from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest


def ajax_required(f):
    """AJAX required decorator.

    Source: http://djangosnippets.org/snippets/771/
    """

    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest
        return f(request, *args, **kwargs)

    return wrap


def tender_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_tender(request.organization)):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrap


def planner_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_planner(request.organization)):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrap


def manager_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_manager(request.organization)):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrap
