from __future__ import unicode_literals
import datetime

from django.utils import timezone

from .common import format_authorization, format_order
from apps.billing.models import Authorization, PriceGroup, PermanentProduct, ProductGroup, TemporaryProduct, \
    Order, Purchase
from apps.scheduling.models import Event
from utils.tests import TestCase


class CommonTest(TestCase):
    def setUp(self):
        super(CommonTest, self).setUp()
        self.load_organization_data()

    def test_authorization_with_account(self):
        """
        Test the authorization.list call.
        """

        # '2014-09-21T14:16:06+00:00'
        start_date = timezone.make_aware(datetime.datetime(2014, 9, 21, 14, 16, 6), timezone.utc)

        # Create authorization
        auth = Authorization(user=self.data['user1'], organization=self.data['organization1'], account='NL13TEST0123456789',
                             start_date=start_date)

        auth_json = {
            'id': auth.id,
            'user': self.data['user1'].username,
            'start_date': '2014-09-21T14:16:06+00:00',
            'end_date': None,
            'account': 'NL13TEST0123456789',
        }

        self.convertAndAssertJSONEqual(format_authorization(auth), auth_json)

    def test_authorization_without_account(self):
        """
        Test the authorization.list call.
        """

        # '2014-09-21T14:16:06+00:00'
        start_date = timezone.make_aware(datetime.datetime(2014, 9, 21, 14, 16, 6), timezone.utc)

        # Create authorization
        auth = Authorization(user=self.data['user1'], organization=self.data['organization1'], account=None,
                             start_date=start_date)

        auth_json = {
            'id': auth.id,
            'user': self.data['user1'].username,
            'start_date': '2014-09-21T14:16:06+00:00',
            'end_date': None,
            'account': None,
        }

        self.convertAndAssertJSONEqual(format_authorization(auth), auth_json)

    def test_authorization_ended(self):
        """
        Test the authorization.list call.
        """

        # '2014-09-21T14:16:06+00:00'
        start_date = timezone.make_aware(datetime.datetime(2014, 9, 21, 14, 16, 6), timezone.utc)
        # '2015-04-16T02:56:33+00:00'
        end_date = timezone.make_aware(datetime.datetime(2015, 4, 16, 2, 56, 33), timezone.utc)

        # Create authorization
        auth = Authorization(user=self.data['user1'], organization=self.data['organization1'], account='NL13TEST0123456789',
                             start_date=start_date, end_date=end_date)

        auth_json = {
            'id': auth.id,
            'user': self.data['user1'].username,
            'start_date': '2014-09-21T14:16:06+00:00',
            'end_date': '2015-04-16T02:56:33+00:00',
            'account': 'NL13TEST0123456789',
        }

        self.convertAndAssertJSONEqual(format_authorization(auth), auth_json)

    def test_order_unsynchronized(self):
        starts_at = timezone.make_aware(datetime.datetime(2014, 9, 21, 14, 16, 6), timezone.utc)
        ends_at = starts_at + datetime.timedelta(hours=1)

        placed_at = starts_at + datetime.timedelta(minutes=30)
        placed_at_string = '2014-09-21T14:46:06+00:00'

        pricegroup = PriceGroup(organization=self.data['organization1'], name='Price group')
        pricegroup.save()

        event = Event(organizer=self.data['organization1'], name='Test event', starts_at=starts_at, ends_at=ends_at,
                      pricegroup=pricegroup, kegs=1)
        event.save()

        productgroup = ProductGroup(organization=self.data['organization1'], name='Product group')
        productgroup.save()

        product1 = PermanentProduct(productgroup=productgroup, organization=self.data['organization1'], position=0)
        product1.save()
        product2 = TemporaryProduct(event=event, price=2.33)
        product2.save()

        authorization = Authorization(user=self.data['user1'], organization=self.data['organization1'], start_date=starts_at)
        authorization.save()

        order = Order(event=event, authorization=authorization, placed_at=placed_at, added_by=self.data['user1'])
        order.save()

        Purchase(order=order, product=product1, amount=1, price=0.50).save()
        Purchase(order=order, product=product2, amount=2, price=4.66).save()
        order.save()

        order_json = {
            'id': order.id,
            'rfid': None,
            'event': {
                'id': event.id,
                'name': 'Test event',
            },
            'authorization': format_authorization(authorization),
            'synchronized': False,
            'placed_at': placed_at_string,
            'purchases': [
                {
                    'product': {
                        'id': product1.id,
                        'name': '',
                    },
                    'amount': 1,
                    'price': '0.50',
                },
                {
                    'product': {
                        'id': product2.id,
                        'name': '',
                    },
                    'amount': 2,
                    'price': '4.66',
                }
            ],
        }

        self.convertAndAssertJSONEqual(format_order(order), order_json)
