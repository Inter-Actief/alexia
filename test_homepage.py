from django.test import Client
from utils.tests import TestCase


class HomepageTest(TestCase):
    def setUp(self):
        super(HomepageTest, self).setUp()
        
        # Every test needs a client.
        self.client = Client()

    def test_homepage_empty(self):
        """
        Test the homepage without data.
        """

        # Issue a GET request.
        response = self.client.get('/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        """
        Test the homepage with data.
        """
        self.load_organization_data()
        self.load_billing_data()
        self.load_scheduling_data()

        # Issue a GET request.
        response = self.client.get('/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
