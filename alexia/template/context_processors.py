from __future__ import unicode_literals

from alexia.apps.organization.models import Membership, Organization


def organization(request):
    return {
        'organizations': Organization.objects.all(),
        'current_organization': request.organization,
    }


def permissions(request):
    if request.user.is_superuser:
        return {'is_tender': True, 'is_planner': True, 'is_manager': True, 'is_foundation_manager': True}

    try:
        if hasattr(request.user, "membership_set"):
            membership = request.user.membership_set.get(organization=request.organization)
       	    return {
                'is_tender': membership.is_tender,
                'is_planner': membership.is_planner,
                'is_manager': membership.is_manager,
                'is_foundation_manager': request.user.profile.is_foundation_manager,
            }
        else:
            return {
                'is_tender': False,
                'is_planner': False,
                'is_manager': False,
                'is_foundation_manager': False,
            }
    except Membership.DoesNotExist:
        return {
            'is_tender': False,
            'is_planner': False,
            'is_manager': False,
            'is_foundation_manager': False,
        }
