import logging
import os
import requests
import sys
import time
from unittest import TestCase
from requests.exceptions import ConnectionError

from ci.builders import ContainerBuilder
from ci.contexts import ContainerBuildContext

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

class ContainerTestCase(TestCase):
    def setUp(self):
        self.context = ContainerBuildContext(
            edge_settings_file=EDGE_SETTINGS_FILE
        )
        self.builder = ContainerBuilder(self.context)
        self.builder.cleanup()
        self.builder.start_container(daemon=True)
    
    def tearDown(self):
        self.builder.cleanup()

    def test_container_application(self):
        for retry in range(RETRIES):
            try:
                response = requests.get("http://localhost:8888/")
                break
            except ConnectionError:
                LOG.info(f"Retry #{retry}")
                time.sleep(BACKOFF)
        self.assertEqual(response.status_code, 200)
        response = requests.get("http://localhost:8888/oauth_start/")
        self.assertEqual(response.status_code, 501)
        response = requests.get("http://localhost:8888/oauth_callback/")
        self.assertEqual(response.status_code, 401)
        response = requests.get("http://localhost:8888/oauth_status/")
        self.assertEqual(response.status_code, 404)