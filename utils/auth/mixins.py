"""
This module contains mixins for Django class-based views handling authorization tests.
"""

from abc import abstractmethod

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _


class PassesTestMixin(object):
    """
    Mixin for validating a access requirement for a view.
    """
    needs_login = False
    """ Indicates if a current login is required for accessing this page. """
    reason = ''
    """ The reason to be returned when the requirement for accessing this page is failed. """

    @abstractmethod
    def test_requirement(self, request):
        """
        Test the requirement for accessing this page.
        This function should return True if accessing this page is allowed.
        """
        return True

    def dispatch(self, request, *args, **kwargs):
        url = u'%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, urlquote(request.get_full_path()))
        if self.needs_login and not request.user.is_authenticated():
            return HttpResponseRedirect(url)
        else:
            if not self.test_requirement(request):
                return render(request, "403.html", {'reason': self.reason}, status=403)
            else:
                return super(PassesTestMixin, self).dispatch(request, *args, **kwargs)


class RequireAjaxMixin(PassesTestMixin):
    reason = _('AJAX-request required')

    def test_requirement(self, request):
        return request.is_ajax()


class TenderRequiredMixin(PassesTestMixin):
    """
    Mixin to require the current user to be a tender of the selected organization.
    """
    needs_login = True
    reason = _('You are not a tender of the selected organization.')

    def test_requirement(self, request):
        return request.user.is_superuser or (request.organization and
                                             request.user.profile.is_tender(request.organization))


class PlannerRequiredMixin(PassesTestMixin):
    """
    Mixin to require the current user to be a planner of the selected organization.
    """
    needs_login = True
    reason = _('You are not a planner of the selected organization.')

    def test_requirement(self, request):
        return request.user.is_superuser or (request.organization and
                                             request.user.profile.is_planner(request.organization))


class ManagerRequiredMixin(PassesTestMixin):
    """
    Mixin to require the current user to be a manager of the selected organization.
    """
    needs_login = True
    reason = _('You are not a manager of the selected organization.')

    def test_requirement(self, request):
        return request.user.is_superuser or (request.organization and
                                             request.user.profile.is_manager(request.organization))


class FoundationManagerRequiredMixin(PassesTestMixin):
    """
    Mixin to require the current user to be a foundation manager.
    """
    needs_login = True
    reason = _('You are not a foundation manager.')

    def test_requirement(self, request):
        return request.user.is_superuser or request.user.profile.is_foundation_manager()
