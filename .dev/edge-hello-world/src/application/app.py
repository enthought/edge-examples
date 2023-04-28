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
from datetime import datetime, timezone
from functools import wraps

import requests
from edge.api import EdgeSession
from flask import Flask

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

JUPYTERHUB_ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
JUPYTERHUB_SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
JUPYTERHUB_API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN")

NATIVE_APP_MODE = os.environ.get("NATIVE_APP_MODE")

EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL")
EDGE_API_ORG = os.environ.get("EDGE_API_ORG")
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

    if (
        _EDGE_SESSION is None
        and EDGE_API_SERVICE_URL
        and EDGE_API_ORG
        and JUPYTERHUB_API_TOKEN
    ):
        _EDGE_SESSION = EdgeSession()
    return _EDGE_SESSION


def track_activity(f):
    """Decorator for reporting server activities with the Hub"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if NATIVE_APP_MODE == "container" or NATIVE_APP_MODE == "dev":
            return f(*args, **kwargs)
        last_activity = datetime.now()
        # Format this in a format that JupyterHub understands
        if last_activity.tzinfo:
            last_activity = last_activity.astimezone(timezone.utc).replace(tzinfo=None)
        last_activity = last_activity.isoformat() + "Z"
        if JUPYTERHUB_ACTIVITY_URL:
            try:
                requests.post(
                    JUPYTERHUB_ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {JUPYTERHUB_API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "servers": {
                            JUPYTERHUB_SERVER_NAME: {"last_activity": last_activity}
                        }
                    },
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


def create_app():
    app = Flask(__name__)

    @app.route("/")
    @track_activity
    def hello_world():
        """The main handle to serve the index page."""
        edge = get_edge_session()
        greeting = "Hello World"
        if edge is not None:
            greeting = greeting + " from Edge"
        return greeting

    return app
