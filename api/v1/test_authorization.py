from __future__ import unicode_literals

from .common import format_authorization
from utils.tests import APITestCase


class AuthorizationTest(APITestCase):
    def test_authorization_list_empty(self):
        """
        Test the authorization.list call with no authorizations.
        """
        self.send_and_compare_request('authorization.list', [], [])
        self.send_and_compare_request('authorization.list', [self.data['user1'].username], [])
        self.send_and_compare_request('authorization.list', [self.data['user2'].username], [])

    def test_authorization_list(self):
        """
        Test the authorization.list call.
        """
        self.load_billing_data()

        auth = self.data['authorization1']
        auth_json = format_authorization(auth)

        self.send_and_compare_request('authorization.list', [], [auth_json])
        self.send_and_compare_request('authorization.list', [self.data['user1'].username], [auth_json])
        self.send_and_compare_request('authorization.list', [self.data['user2'].username], [])

    def test_authorization_list_invalid_user(self):
        """
        Test the authorization.list call with invalid username.
        """
        # Invalid user
        self.send_and_compare_request_error('authorization.list', ['invalidusername'],
                                            error_code=-32602,
                                            error_name='InvalidParametersError',
                                            error_message='InvalidParametersError: User with provided radius_username does not exits',
                                            )
