# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import datetime
import logging
import multiprocessing as mp
import os
import sys
from functools import wraps
from uuid import uuid4
from urllib.parse import unquote

import requests
from flask import Flask, make_response, redirect, render_template, request, session
from flask_session import Session
from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import isoformat


# When running flask in debug mode outside of a JupyterHub environment,
# deactivate the `authenticated` and `track_activity` decorator.
FLASK_DEBUG = int(os.environ.get("FLASK_DEBUG", 0))

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)
if FLASK_DEBUG:
    LOG.setLevel(logging.DEBUG)

# When run from Edge, these environment variables will be provided
PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
API_URL = os.environ.get("JUPYTERHUB_API_URL", "http://127.0.0.1:8081")
APP_VERSION = os.environ.get("APP_VERSION", "native-app-example")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL", None)
EDGE_API_ORG = os.environ.get("EDGE_API_ORG", None)

#AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)

LOG.debug(f"JUPYTERHUB_SERVER_NAME {SERVER_NAME}")
LOG.debug(f"JUPYTERHUB_SERVICE_PREFIX {PREFIX}")
LOG.debug(f"JUPYTERHUB_ACTIVITY_URL {ACTIVITY_URL}")


def create_app():
    """Creates the Flask app with routes for serving the React application
    and API routes for running jobs
    """
    mp.set_start_method("spawn")  # Starts a fresh process instead of forking.
    manager = mp.Manager()

    # Use a multiprocessing shared dictionary for aggregating job results

    app = Flask(
        __name__,
    )
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SECRET_KEY"] = "super secret key"
    sess = Session()
    sess.init_app(app)

    @app.route("/oauth_callback")
    def oauth_callback(**kwargs):
        return "OK", 202

    return app
