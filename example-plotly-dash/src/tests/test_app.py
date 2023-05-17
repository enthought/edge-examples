from unittest import TestCase

from application.app import server


class TestHelloWorld(TestCase):
    def setUp(self):
        self.client = server.test_client()

    def test_hello_world(self):
        response = self.client.get("/")
        # Assert that the Flask app serves the React app
        # bootstrap
        self.assertIn("DashRenderer", response.text)
