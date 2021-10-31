"""
Contains unit tests for verifying correct functionality of functions used in the application.
"""
from django.test import TestCase, Client


class URLTestCase(TestCase):
    """
    Test methods making sure that URLs behave correctly.
    """

    def test_index_page(self):
        """
        Double-checks that the index page responds by correctly redirecting to Login.
        """
        c = Client()
        return_response = c.get("/")
        self.assertEqual(return_response.status_code, 302)
