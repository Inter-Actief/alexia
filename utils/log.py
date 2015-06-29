"""Logfuncties voor loggen van wijzigingen in borrels,
tapper-beschikbaarheid en tappers.

Met deze functies kan het aanmaken,  wijzigen en verwijderen van
borrels, tappers en tapper-beschikbaarheid gelogd worden op hetzelfde
niveau als dat ook in het oude borrelbeheersysteem gedaan werd.

Deze functies worden aangeroepen vanuit de views die de wijzigingen
uitvoeren. Wijzigingen via de API worden op moment van schrijven nog
niet gelogd.

Auteur: Jelte Zeilstra
"""

from eventlog.models import log


def event_created(user, event):
    """Log het aanmaken van een borrel."""
    log(user, 'CREATED_EVENT', {"pk": event.pk, "name": event.name})


def event_modified(user, event):
    """Log het wijzigen van een borrel."""
    log(user, 'MODIFIED_EVENT', {"pk": event.pk, "name": event.name})


def event_deleted(user, event):
    """Log het verwijderen van een borrel."""
    log(user, 'DELETED_EVENT', {"pk": event.pk, "name": event.name})


def availability_created(user, event, bartender, availability):
    """Log het aanmaken van een BartenderAvailability."""
    log(user, 'CREATED_AVAILABILITY', {"pk": event.pk,
                                       "bartender": bartender.get_full_name(),
                                       "availability": availability.__unicode__()})


def availability_changed(user, event, bartender, old_availability, new_availability):
    """Log het wijzigen van een BartenderAvailability."""
    log(user, 'MODIFIED_AVAILABILITY', {"pk": event.pk,
                                        "bartender": bartender.get_full_name(),
                                        "old_availability": old_availability.__unicode__(),
                                        "new_availability": new_availability.__unicode__()})


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
    """Log het aanmaken van een Membership."""
    log(user, 'CREATED_MEMBERSHIP', {"membership": membership.__unicode__(),
                                     "roles": _roles(membership)})


def membership_modified(user, membership):
    """Log het wijzigen van een Membership."""
    log(user, 'MODIFIED_MEMBERSHIP', {"membership": membership.__unicode__(),
                                      "roles": _roles(membership)})


def membership_deleted(user, membership):
    """Log het verwijderen van een Membership."""
    log(user, 'DELETED_MEMBERSHIP', {"membership": membership.__unicode__()})
