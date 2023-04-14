import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlencode

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from alexia.apps.organization.models import AuthenticationData, Profile

User = get_user_model()
OIDC_BACKEND_NAME = 'utils.auth.backends.oidc.OIDCBackend'


def get_or_create_user(backend, username):
    try:
        authentication_data = AuthenticationData.objects.get(backend=backend, username=username)
        return authentication_data.user, False
    except AuthenticationData.DoesNotExist:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
            user.set_unusable_password()
            user.save()

        data = AuthenticationData(user=user, backend=backend, username=username.lower())
        data.save()

        if not user.profile:
            profile = Profile(user=user)
            profile.save()

        return user, True


class IAOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

    def verify_claims(self, claims):
        """Block login if the OIDC claims do not give a value for a UT username we support"""
        # UT Student number
        has_student_number = claims.get('studentNumber', None) is not None
        # UT Employee number
        has_employee_number = claims.get('employeeNumber', None) is not None
        # UT X-account username
        has_ut_xaccount = claims.get('externalUsername', None) is not None

        can_continue = has_student_number or has_employee_number or \
            has_ut_xaccount
        self.log.debug(f"User login claims verification can continue: {can_continue}, with claims: {claims}")
        return can_continue

    def filter_users_by_claims(self, claims):
        # UT Student number
        student_username = claims.get('studentNumber', None)
        student_username = student_username.lower() if student_username else None
        # UT Employee number
        employee_username = claims.get('employeeNumber', None)
        employee_username = employee_username.lower() if employee_username else None
        # UT X-account username
        ut_xaccount = claims.get('externalUsername', None)
        ut_xaccount = ut_xaccount.lower() if ut_xaccount else None

        # Try to find person by Student number
        if student_username is not None:
            user, created = get_or_create_user(OIDC_BACKEND_NAME, student_username)
            self.log.info(f"User login to {'new' if created else 'existing'} user {user.username} with S-number {student_username} allowed.")
            return [user]

        # Try to find person by Employee number
        if employee_username is not None:
            user, created = get_or_create_user(OIDC_BACKEND_NAME, employee_username)
            self.log.info(f"User login to {'new' if created else 'existing'} user {user.username} with M-number {employee_username} allowed.")
            return [user]

        # Try to find person by X-account username
        if ut_xaccount is not None:
            user, created = get_or_create_user(OIDC_BACKEND_NAME, ut_xaccount)
            self.log.info(f"User login to {'new' if created else 'existing'} user {user.username} with X-number {ut_xaccount} allowed.")
            return [user]

        # No cigar.
        self.log.info(f"User login failed, no username found to match against.")
        return self.UserModel.objects.none()


def get_oidc_logout_url(request):
    # After logout, we need to redirect to the OIDC Single Sign Out
    # endpoint (OIDC_LOGOUT_URL) with a redirect back to the main page
    params = urlencode({
        'id_token_hint': request.session.get("oidc_id_token", ""),
        'post_logout_redirect_uri': request.build_absolute_uri(reverse("event-list"))
    })
    return f"{settings.OIDC_LOGOUT_URL}?{params}"
