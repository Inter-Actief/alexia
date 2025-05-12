from alexia.apps.billing.models import Order
from alexia.test import APITestCase

from ..common import format_order


class BillingTest(APITestCase):

    def test_order_unsynchronized_empty(self):
        self.send_and_compare_request('order.unsynchronized', [0], [])

    def test_order_unsynchronized_with_parameter(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        expected_result = [
            format_order(self.data['order1']),
            format_order(self.data['order2']),
        ]

        self.send_and_compare_request('order.unsynchronized', [0], expected_result)

    def test_order_unsynchronized_without_parameter(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        expected_result = [
            format_order(self.data['order1']),
            format_order(self.data['order2']),
        ]

        self.send_and_compare_request('order.unsynchronized', [], expected_result)

    def test_order_unsynchronized_synchronized(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        self.data['order1'].synchronized = True
        self.data['order1'].save()

        expected_result = [
            format_order(self.data['order2']),
        ]

        self.send_and_compare_request('order.unsynchronized', [0], expected_result)

    def test_order_marksynchronized(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        self.send_and_compare_request('order.marksynchronized', [self.data['order1'].id], True)

        self.assertTrue(Order.objects.get(id=self.data['order1'].id).synchronized)

    def test_order_marksynchronized_synchronized(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        self.data['order1'].synchronized = True
        self.data['order1'].save()

        self.send_and_compare_request('order.marksynchronized', [self.data['order1'].id], False)

        self.assertTrue(Order.objects.get(id=self.data['order1'].id).synchronized)

    def test_order_marksynchronized_invalid_order(self):
        # Load data
        self.load_billing_data()
        self.load_scheduling_data()
        self.load_billing_order_data()

        self.send_and_compare_request_error('order.marksynchronized', [self.data['order1'].id*10],
                                            status_code=422,
                                            error_code=-32602,
                                            error_name='InvalidParamsError',
                                            error_message='InvalidParamsError: Order with id not found',
                                            )
