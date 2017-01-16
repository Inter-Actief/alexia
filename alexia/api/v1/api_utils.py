# Helpers

from alexia.auth.backends import RADIUS_BACKEND_NAME


def user_list(organization, objects):
    """Helper function to list users to an array

    organization    -- The organization to filter on
    objects         -- Queryset to query objects from

    """

    result = []
    users = objects.filter(
        organization=organization,
        user__profile__isnull=False).exclude(
        user__authenticationdata__backend=RADIUS_BACKEND_NAME,
        user__authenticationdata__username="")

    for u in users:
        result.append(u.user.authenticationdata_set.get(backend=RADIUS_BACKEND_NAME).username)

    return result


def manager_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser and (
                not request.organization or not request.user.profile.is_manager(request.organization)):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrap
