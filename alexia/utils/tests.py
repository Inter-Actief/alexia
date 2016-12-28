from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.test import Client, testcases
from django.utils import six, timezone

from alexia.apps.billing.models import (
    Authorization, Order, PermanentProduct, PriceGroup, ProductGroup, Purchase,
    TemporaryProduct,
)
from alexia.apps.organization.models import (
    AuthenticationData, Location, Organization, Profile,
)
from alexia.apps.scheduling.models import Availability, Event
from alexia.auth.backends import RADIUS_BACKEND_NAME


class SimpleTestCase(testcases.SimpleTestCase):
    # Use long messages on failure
    longMessage = True
    # Do not limit diff length on failure
    maxDiff = None

    def assertJSONEqual(self, raw, expected_data, msg=None):
        if not isinstance(expected_data, six.string_types):
            # Encode non-string input as JSON to fix a bug timestamps not comparing equal.
            expected_data = json.dumps(expected_data, cls=DjangoJSONEncoder)

        super(SimpleTestCase, self).assertJSONEqual(raw, expected_data, msg)

    def convertAndAssertJSONEqual(self, data, expected_data, msg=None):
        """
        Converts the data to JSON and asserts that the JSON fragments equals the expected_data.
        Usual JSON non-significant whitespace rules apply as the heavyweight
        is delegated to the json library.
        """

        super(SimpleTestCase, self).assertJSONEqual(json.dumps(data, cls=DjangoJSONEncoder), expected_data, msg)


class TransactionTestCase(SimpleTestCase, testcases.TransactionTestCase):
    pass


class TestCase(TransactionTestCase, testcases.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.data = dict()

        self.data['datetime1'] = timezone.make_aware(datetime.datetime(2014, 9, 21, 14, 16, 6), timezone.utc)
        self.data['datetime2'] = self.data['datetime1'] + datetime.timedelta(hours=1)
        self.data['datetime3'] = self.data['datetime1'] + datetime.timedelta(hours=2)

        self.data['datetime1_string'] = '2014-09-21T14:16:06+00:00'
        self.data['datetime2_string'] = '2014-09-21T15:16:06+00:00'
        self.data['datetime3_string'] = '2014-09-21T16:16:06+00:00'

    def load_organization_data(self):
        data = self.data

        # User / Profile
        username1 = 'testuser'
        username2 = 'testuser2'

        data['password1'] = 'testuser13475'
        data['password2'] = 'testuser23475'

        data['user1'] = User(username=username1, first_name='Test', last_name='Client', email='test@example.com',
                             is_superuser=True)
        data['user1'].set_password(data['password1'])
        data['user1'].save()

        data['user1'].profile = Profile()
        data['user1'].profile.save()

        data['authenticationdata1'] = AuthenticationData(backend=RADIUS_BACKEND_NAME, username=username1,
                                                         user=data['user1'])
        data['authenticationdata1'].save()

        data['user2'] = User(username=username2, first_name='Test2', last_name='Client', email='test2@example.com')
        data['user2'].set_password(data['password2'])
        data['user2'].save()

        data['user2'].profile = Profile()
        data['user2'].profile.save()

        data['authenticationdata2'] = AuthenticationData(backend=RADIUS_BACKEND_NAME, username=username2,
                                                         user=data['user2'])
        data['authenticationdata2'].save()

        # Organization
        data['organization1'] = Organization(name='Organization 1')
        data['organization1'].save()

        data['organization2'] = Organization(name='Organization 2')
        data['organization2'].save()

        # Location
        data['location1'] = Location(name='Location 1', is_public=True, prevent_conflicting_events=True)
        data['location1'].save()

        data['location2'] = Location(name='Location 2', is_public=True, prevent_conflicting_events=False)
        data['location2'].save()

    def load_billing_data(self):
        data = self.data

        data['pricegroup1'] = PriceGroup(organization=data['organization1'], name='Price group 1')
        data['pricegroup1'].save()

        data['productgroup1'] = ProductGroup(organization=data['organization1'], name='Product group 1')
        data['productgroup1'].save()

        data['permantentproduct1'] = PermanentProduct(productgroup=data['productgroup1'],
                                                      organization=data['organization1'],
                                                      position=0)
        data['permantentproduct1'].save()

        data['authorization1'] = Authorization(user=data['user1'],
                                               organization=data['organization1'],
                                               start_date=data['datetime1'])
        data['authorization1'].save()

    def load_scheduling_data(self):
        data = self.data

        data['availability1'] = Availability(organization=data['organization1'],
                                             name='Yes',
                                             nature=Availability.ASSIGNED)
        data['availability1'].save()

        data['availability2'] = Availability(organization=data['organization1'],
                                             name='Maybe',
                                             nature=Availability.MAYBE)
        data['availability2'].save()

        data['availability3'] = Availability(organization=data['organization1'],
                                             name='No',
                                             nature=Availability.NO)
        data['availability3'].save()

        data['event1'] = Event(organizer=data['organization1'],
                               name='Test event 1',
                               starts_at=data['datetime1'],
                               ends_at=data['datetime3'],
                               pricegroup=data['pricegroup1'],
                               kegs=1)
        data['event1'].save()

        data['temporaryproduct1'] = TemporaryProduct(event=data['event1'], price=2.33)
        data['temporaryproduct1'].save()

    def load_billing_order_data(self):
        data = self.data

        data['order1'] = Order(event=data['event1'], authorization=data['authorization1'], placed_at=data['datetime2'],
                               added_by=data['user1'])
        data['order1'].save()

        Purchase(order=data['order1'], product=data['permantentproduct1'], amount=1, price=0.50).save()
        Purchase(order=data['order1'], product=data['temporaryproduct1'], amount=2, price=4.66).save()
        data['order1'].save()

        data['order2'] = Order(event=data['event1'], authorization=data['authorization1'], placed_at=data['datetime2'],
                               added_by=data['user1'])
        data['order2'].save()

        Purchase(order=data['order2'], product=data['permantentproduct1'], amount=3, price=1.50).save()
        Purchase(order=data['order2'], product=data['temporaryproduct1'], amount=4, price=9.32).save()
        data['order2'].save()


class APITestCase(TestCase):
    def setUp(self):
        super(APITestCase, self).setUp()

        self.load_organization_data()

        # Every test needs a client.
        self.client = Client()
        self.login(username=self.data['user1'].username,
                   password=self.data['password1'],
                   organization_slug=self.data['organization1'].slug)

    def login(self, username, password, organization_slug=None):
        """
        Login the test client.
        :param username: Username
        :param password: Password
        :param organization_slug: Slug of organization to set as current organization.
        """

        self.client.login(username=username, password=password)
        self.send_and_compare_request('organization.current.set', [organization_slug], True)

    def send_request(self, method, params):
        """
        Send JSON RPC method call.
        :param method: Name of method to call.
        :param params: Parameters for JSON RPC call.
        :rtype : django.http.response.HttpResponse
        """
        path = reverse('api_v1_mountpoint')

        req = {
            'jsonrpc': '1.0',
            'id': 'jsonrpc',
            'method': method,
            'params': params,
        }

        req_json = json.dumps(req)
        return self.client.post(path, req_json, content_type='text/plain; charset=UTF-8')

    def send_and_compare_request(self, method, params, expected_result):
        """
        Send JSON RPC method call and compare actual result with expected result.
        :param method: Name of method to call.
        :param params: Parameters for JSON RPC call.
        :param expected_result: Expected result.
        """

        response = self.send_request(method, params)

        self.assertEqual(response['Content-Type'], 'application/json-rpc')

        content = response.content.decode('utf-8')

        expected_data = {
            'jsonrpc': '1.0',
            'id': 'jsonrpc',
            'error': None,
            'result': expected_result,
        }

        self.assertJSONEqual(content, expected_data)

    def send_and_compare_request_error(self, method, params, error_code, error_name, error_message, error_data=None,
                                       status_code=200):
        """
        Send JSON RPC method call and compare actual error result with expected error result.
        :param method: Name of method to call.
        :param params: Parameters for JSON RPC call.
        :param error_code: Expected error code.
        :param error_name: Expected error name.
        :param error_message: Expected error message.
        :param error_data: Expected error data.
        :param status_code: Expected HTTP status code.
        """
        response = self.send_request(method, params)

        if response.status_code != status_code:
            self.fail(response.content)

        self.assertEqual(response.status_code, status_code, 'HTTP status code')

        self.assertEqual(response['Content-Type'], 'application/json-rpc')

        content = response.content.decode('utf-8')

        expected_data = {
            'jsonrpc': '1.0',
            'id': 'jsonrpc',
            'error': {
                'code': error_code,
                'name': error_name,
                'message': error_message,
                'data': error_data,
            },
            'result': None,
        }

        self.assertJSONEqual(content, expected_data, 'JSON RPC result')
