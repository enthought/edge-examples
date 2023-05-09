import logging
import os
import sys
import time
from unittest import TestCase
from urllib.parse import urlparse

import requests

from ci.builders import PreflightBuilder
from ci.contexts import PreflightBuildContext

formatter = logging.Formatter(
    "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s"
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
LOG = logging.getLogger()
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


EDGE_SETTINGS_FILE = os.environ.get("EDGE_SETTINGS_FILE")
RETRIES = 5
BACKOFF = 5


class PreflightTestCase(TestCase):
    def setUp(self):
        self.context = PreflightBuildContext(edge_settings_file=EDGE_SETTINGS_FILE)
        self.builder = PreflightBuilder(self.context)
        self.builder.cleanup()
        self.process = self.builder.start_jupyterhub()

        # Wait for JupyterHub to start correctly
        time.sleep(BACKOFF * 2)
        self.process.poll()
        if self.process.returncode is not None:
            self.process.terminate()
            raise AssertionError("JupyterHub failed to start")

    def tearDown(self):
        self.builder.cleanup()
        self.process.terminate()

    def test_preflight(self):
        # Perform requests with session to save jupyterhub session cookies
        with requests.Session() as s:
            # Get the login page
            s.get("http://localhost:8000/hub/login")
            # Perform a login
            response = s.post(
                "http://localhost:8000/hub/login",
                data={"username": "edgeuser", "password": "password"},
                allow_redirects=True,
            )
            # Start the spawner
            response = s.get("http://localhost:8000/hub/spawn/edgeuser")
            # Collate all redirects
            redirects = []
            for _ in range(RETRIES):
                response = s.get("http://localhost:8000/user/edgeuser")
                redirects = redirects + [urlparse(r.url).path for r in response.history]
                if "spawn-pending" in response.url:
                    LOG.info("Waiting for single user server to spawn")
                    time.sleep(BACKOFF)
            response = s.get("http://localhost:8000/user/edgeuser")
            redirects = redirects + [urlparse(r.url).path for r in response.history]

            # Assert that the authentication flow redirects are present
            self.assertIn("/user/edgeuser/oauth_start/", redirects)
            self.assertIn("/hub/api/oauth2/authorize", redirects)
            self.assertIn("/user/edgeuser/oauth_callback/", redirects)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.url, "http://localhost:8000/user/edgeuser/")

        # Perform a second test after the hub has spawned to validate
        # that unauthenticated users cannot access the server
        response = requests.get(
            "http://localhost:8000/user/edgeuser/", allow_redirects=True
        )
        self.assertNotEqual(response.url, "http://localhost:8000/user/edgeuser/")
