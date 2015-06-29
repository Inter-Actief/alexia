# Helpers
def user_list(organization, objects):
    """Helper function to list users to an array

    organization    -- The organization to filter on
    objects         -- Queryset to query objects from

    """

    result = []
    users = objects.filter(
        organization=organization,
        user__profile__isnull=False).exclude(
        user__profile__radius_username="")

    for u in users:
        result.append(u.user.profile.radius_username)

    return result
