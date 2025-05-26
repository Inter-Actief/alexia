import datetime

from django.test.testcases import SimpleTestCase
from django.utils import timezone

from alexia.api.exceptions import ForbiddenError, InvalidParamsError
from alexia.apps.billing.models import RfidCard
from alexia.test import APITestCase, TestCase

from ..common import format_authorization
from ..methods.juliana import _get_validate_event, rfid_to_identifier


class JulianaRfidToIdentifierTest(SimpleTestCase):
    """
    Tests for the api.v1.juliana.rfid_to_identifier method.
    """

    def test_mifare_clasic_1k(self):
        rfid = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }
        self.assertEqual(rfid_to_identifier(rfid), '02,98:ab:54:ef')

    def test_mifare_clasic_4k(self):
        rfid = {
            'atqa': '00:02',
            'sak': '18',
            'uid': '98:ab:54:ef',
        }
        self.assertEqual(rfid_to_identifier(rfid), '03,98:ab:54:ef')

    def test_mifare_clasic_desfire(self):
        rfid = {
            'atqa': '03:44',
            'sak': '20',
            'uid': '98:ab:54:ef:10:cb:76',
        }
        self.assertEqual(rfid_to_identifier(rfid), '04,98:ab:54:ef:10:cb:76')

    def test_mifare_clasic_ultralight(self):
        rfid = {
            'atqa': '00:44',
            'sak': '00',
            'uid': '98:ab:54:ef:10:cb:76',
        }
        self.assertEqual(rfid_to_identifier(rfid), '05,98:ab:54:ef:10:cb:76')

    def test_mifare_invalid_combination(self):
        rfid = {
            'atqa': '00:05',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }
        with self.assertRaises(InvalidParamsError):
            rfid_to_identifier(rfid)

    def test_mifare_no_atqa(self):
        rfid = {
            'sak': '08',
            'uid': '98:ab:54:ef',
        }
        with self.assertRaises(InvalidParamsError):
            rfid_to_identifier(rfid)

    def test_mifare_no_sak(self):
        rfid = {
            'atqa': '00:04',
            'uid': '98:ab:54:ef',
        }
        with self.assertRaises(InvalidParamsError):
            rfid_to_identifier(rfid)

    def test_mifare_no_uid(self):
        rfid = {
            'atqa': '00:04',
            'sak': '08',
        }
        with self.assertRaises(InvalidParamsError):
            rfid_to_identifier(rfid)


class JulianaGetValidateEventTest(TestCase):
    """
    Tests for the api.v1.juliana._get_validate_event method.
    """

    def setUp(self):
        super(JulianaGetValidateEventTest, self).setUp()
        self.load_organization_data()
        self.load_billing_data()
        self.load_scheduling_data()

        data = self.data

        # Make event1 current
        now = timezone.now()
        self.data['event1'].starts_at = now - datetime.timedelta(hours=1)
        self.data['event1'].ends_at = now + datetime.timedelta(hours=1)
        self.data['event1'].save()

        # Add user2 as tender for organization 1
        data['organization1'].membership_set.create(user=data['user2'], is_tender=True)

        # Add user2 as tender for event1
        self.data['event1'].bartender_availabilities.create(user=self.data['user2'],
                                                            availability=self.data['availability1'])

        class MockRequest(object):
            def __init__(self, user):
                super(MockRequest, self).__init__()
                self.user = user

        self.request = MockRequest(self.data['user2'])

    def test_normal(self):
        event_id = self.data['event1'].id
        self.assertEqual(_get_validate_event(self.request, event_id), self.data['event1'])

    def test_no_event(self):
        event_id = self.data['event1'].id * 100

        with self.assertRaises(InvalidParamsError):
            _get_validate_event(self.request, event_id)

    def test_no_tender(self):
        event_id = self.data['event1'].id

        # Mark bartender as not available
        bartender_availability = self.data['event1'].bartender_availabilities.get(user=self.data['user2'])
        bartender_availability.availability = self.data['availability3']
        bartender_availability.save()

        with self.assertRaises(ForbiddenError):
            _get_validate_event(self.request, event_id)

    def test_event_past(self):
        event_id = self.data['event1'].id

        # Make event in the past
        now = timezone.now()
        self.data['event1'].starts_at = now - datetime.timedelta(days=1, hours=2)
        self.data['event1'].ends_at = now - datetime.timedelta(days=1, hours=1)
        self.data['event1'].save()

        with self.assertRaises(ForbiddenError):
            _get_validate_event(self.request, event_id)

    def test_event_future(self):
        event_id = self.data['event1'].id

        # Make event in the future
        now = timezone.now()
        self.data['event1'].starts_at = now + datetime.timedelta(days=1, hours=1)
        self.data['event1'].ends_at = now + datetime.timedelta(days=1, hours=2)
        self.data['event1'].save()

        with self.assertRaises(ForbiddenError):
            _get_validate_event(self.request, event_id)

    def test_superuser(self):
        event_id = self.data['event1'].id

        # Make event in the future
        now = timezone.now()
        self.data['event1'].starts_at = now + datetime.timedelta(days=1, hours=1)
        self.data['event1'].ends_at = now + datetime.timedelta(days=1, hours=2)
        self.data['event1'].save()

        # Login superuser
        self.request.user = self.data['user1']

        # Call should still be allowed
        self.assertEqual(_get_validate_event(self.request, event_id), self.data['event1'])


class JulianaTest(APITestCase):
    """
    Tests for the api.v1.juliana API methods.
    """

    def setUp(self):
        super(JulianaTest, self).setUp()
        self.load_billing_data()
        self.load_scheduling_data()

        data = self.data

        # Make event1 current
        now = timezone.now()
        self.data['event1'].starts_at = now - datetime.timedelta(hours=1)
        self.data['event1'].ends_at = now + datetime.timedelta(hours=1)
        self.data['event1'].save()

        # Add user2 as tender for organization 1
        data['organization1'].membership_set.create(user=data['user2'], is_tender=True)

        # Add user2 as tender for event1
        self.data['event1'].bartender_availabilities.create(user=self.data['user2'],
                                                            availability=self.data['availability1'])

        # Login user2
        self.login(username=self.data['user2'].username,
                   password=self.data['password2'],
                   organization_slug=self.data['organization1'].slug)

    def test_rfid_get(self):
        event_id = self.data['event1'].id

        rfid_data = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }

        self.data['user2'].rfidcard_set.create(identifier='02,98:ab:54:ef', is_active=True)
        authorization = self.data['user2'].authorizations.create(organization=self.data['organization1'])
        # Ignore microseconds
        authorization.start_date = authorization.start_date.replace(microsecond=0)
        authorization.save()

        expected_result = {
            'user': {
                'id': self.data['user2'].id,
                'first_name': self.data['user2'].first_name,
                'last_name': self.data['user2'].last_name,
                'username': self.data['user2'].username,
            },
            'authorization': format_authorization(authorization),
        }

        self.send_and_compare_request('juliana.rfid.get', [event_id, rfid_data], expected_result)

    def test_rfid_get_no_rfid(self):
        event_id = self.data['event1'].id

        rfid_data = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }

        self.send_and_compare_request_error(
            'juliana.rfid.get', [event_id, rfid_data],
            status_code=200,
            error_code=404,
            error_message='RFID card not found',
        )

    def test_rfid_get_no_authorization(self):
        event_id = self.data['event1'].id

        rfid_data = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }

        rfidcard = RfidCard(identifier='02,98:ab:54:ef', is_active=True, user=self.data['user2'])
        rfidcard.save()

        self.send_and_compare_request_error(
            'juliana.rfid.get', [event_id, rfid_data],
            status_code=200,
            error_code=404,
            error_message='No authorization found for user',
        )

    def test_rfid_get_other_authorization(self):
        event_id = self.data['event1'].id

        rfid_data = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }

        self.data['user2'].rfidcard_set.create(identifier='02,98:ab:54:ef', is_active=True)
        self.data['user2'].authorizations.create(organization=self.data['organization2'])

        self.send_and_compare_request_error(
            'juliana.rfid.get', [event_id, rfid_data],
            status_code=200,
            error_code=404,
            error_message='No authorization found for user',
        )

    def test_rfid_get_invalid_event(self):
        event_id = self.data['event1'].id * 100

        rfid_data = {
            'atqa': '00:04',
            'sak': '08',
            'uid': '98:ab:54:ef',
        }

        self.send_and_compare_request_error(
            'juliana.rfid.get', [event_id, rfid_data],
            status_code=200,
            error_code=404,
            error_message='Event does not exist',
        )

    def test_user_check_no_orders(self):
        event_id = self.data['event1'].id
        user_id = self.data['user1'].id
        self.send_and_compare_request('juliana.user.check', [event_id, user_id], 0)

    def test_user_check_with_orders(self):
        # Add some orders to event1
        self.load_billing_order_data()

        event_id = self.data['event1'].id
        user_id = self.data['user1'].id

        expected_amount = self.data['order1'].amount + self.data['order2'].amount
        expected_result = int(expected_amount * 100)

        self.send_and_compare_request('juliana.user.check', [event_id, user_id], expected_result)

    def test_user_check_invalid_event(self):
        event_id = self.data['event1'].id * 100
        user_id = self.data['user1'].id

        self.send_and_compare_request_error(
            'juliana.user.check', [event_id, user_id],
            status_code=200,
            error_code=404,
            error_message='Event does not exist',
        )

    def test_user_check_invalid_user(self):
        event_id = self.data['event1'].id
        user_id = self.data['user1'].id * 100

        self.send_and_compare_request_error(
            'juliana.user.check', [event_id, user_id],
            status_code=200,
            error_code=404,
            error_message='User does not exist',
        )
