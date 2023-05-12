from unittest import TestCase

from application.app import create_app


class TestHelloWorld(TestCase):
    def setUp(self):
        app = create_app()
        self.client = app.test_client()

    def test_hello_world(self):
        response = self.client.get("/")
        # Assert that the Flask app serves the React app
        # bootstrap
        self.assertIn("native-app-example", response.text)
