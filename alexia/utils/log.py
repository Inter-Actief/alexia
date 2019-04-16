from alexia.apps.general.models import log


def event_created(user, event):
    log(user, 'CREATED_EVENT', {"pk": event.pk, "name": event.name})


def event_modified(user, event):
    log(user, 'MODIFIED_EVENT', {"pk": event.pk, "name": event.name})


def event_deleted(user, event):
    log(user, 'DELETED_EVENT', {"pk": event.pk, "name": event.name})


def availability_created(user, event, bartender, availability):
    log(user, 'CREATED_AVAILABILITY', {
        "pk": event.pk,
        "bartender": bartender.get_full_name(),
        "availability": availability.__str__(),
    })


def availability_changed(user, event, bartender, old_availability, new_availability):
    log(user, 'MODIFIED_AVAILABILITY', {
        "pk": event.pk,
        "bartender": bartender.get_full_name(),
        "old_availability": old_availability.__str__(),
        "new_availability": new_availability.__str__(),
    })


def _roles(membership):
    roles = []
    if membership.is_tender:
        roles.append('tender')
    if membership.is_planner:
        roles.append('planner')
    if membership.is_manager:
        roles.append('manager')
    return roles


def membership_created(user, membership):
    log(user, 'CREATED_MEMBERSHIP', {"membership": membership.__str__(), "roles": _roles(membership)})


def membership_modified(user, membership):
    log(user, 'MODIFIED_MEMBERSHIP', {"membership": membership.__str__(), "roles": _roles(membership)})


def membership_deleted(user, membership):
    log(user, 'DELETED_MEMBERSHIP', {"membership": membership.__str__()})
