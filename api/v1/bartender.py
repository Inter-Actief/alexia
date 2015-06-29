from django.contrib.auth.models import User
from jsonrpc import jsonrpc_method

from .api_utils import user_list
from .common import api_v1_site
from apps.organization.forms import BartenderAvailabilityForm
from apps.organization.models import Membership, Profile
from apps.scheduling.models import Event


@jsonrpc_method('bartender.list() -> Array', site=api_v1_site, authenticated=True)
def bartender_list(request):
    """Retrieve a list of users who currently are subscribed as a tender"""
    return user_list(request.organization, Membership.objects)


@jsonrpc_method('bartender.add(String) -> Boolean', site=api_v1_site, authenticated=True)
def bartender_add(request, radius_username):
    """Add an user as bartender for the current organization.

    Returns true when successful

    radius_username    -- RADIUS username to add as bartender
    """
    try:
        Membership.objects.get(
            user__profile__radius_username=radius_username,
            organization=request.organization)
    except Membership.DoesNotExist:
        profile = Profile.objects.get(radius_username=radius_username)
        bartender = Membership(user=profile.user, organization=request.organization)
        bartender.save()

    return True


@jsonrpc_method('bartender.remove(String) -> Boolean', site=api_v1_site, authenticated=True)
def bartender_remove(request, radius_username):
    """Remove a user from the list of bartenders for the current organization

    radius_username    -- RADIUS username to add as bartender
    """
    try:
        Membership.objects.get(
            user__profile__radius_username=radius_username,
            organization=request.organization).delete()
    except Membership.DoesNotExist:
        pass

    return True


@jsonrpc_method('bartender.clear() -> Boolean', site=api_v1_site, authenticated=True)  # TODO: speciale permissie
def bartender_clear(request):
    """Remove a user from the list of bartenders for the current organization

    radius_username    -- RADIUS username to add as bartender
    """
    try:
        Membership.objects.filter(
            organization=request.organization).delete()
    except Membership.DoesNotExist:
        pass

    return True


@jsonrpc_method('bartender.availability.set(Number, Number, Number) -> Boolean', site=api_v1_site,
                authenticated=True)  # TODO: speciale permissie
def bartender_availability_set(request, user_id, event_id, status_id):
    """Changes the availability for the given user and event."""

    try:
        # Get the data from the database
        event = Event.objects.get(pk=event_id)
        user = User.objects.get(pk=user_id)
        form = BartenderAvailabilityForm(event=event, user=user, data={
            "availability": status_id
        })

        if form.is_valid():
            form.save()
            return True
    except:
        pass

    return False
