# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import logging
import os
import sys
import requests
from urllib.parse import urlparse

from flask import Flask
from edge.api import EdgeSession

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)


EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL")
EDGE_API_ORG = os.environ.get("EDGE_API_ORG")
JUPYTERHUB_API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN")
_EDGE_SESSION = None


def get_edge_session():
    """Helper function to get an EdgeSession object
    
    Returns:
        An EdgeSession object, if the environment has
        the EDGE_API_SERVICE_URL, EDGE_API_ORG and JUPYTERHUB_API_TOKEN
        environment variables. If these variables are not set,
        then None is returned
    """
    global _EDGE_SESSION

    if _EDGE_SESSION is None and \
       EDGE_API_SERVICE_URL and EDGE_API_ORG and JUPYTERHUB_API_TOKEN:
        _EDGE_SESSION = EdgeSession()
    return _EDGE_SESSION


def create_app():
    app = Flask(__name__)
    @app.route("/")
    def hello_world():
        """The main handle to serve the index page."""
        edge = get_edge_session()
        greeting = "Hello World"
        if edge is not None:
            greeting = greeting + " from Edge"
        return greeting

    return app
