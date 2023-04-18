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
LOG.setLevel(logging.DEBUG)

# When run from Edge, these environment variables will be provided
PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
API_URL = os.environ.get("JUPYTERHUB_API_URL")
JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL", None)
EDGE_API_ORG = os.environ.get("EDGE_API_ORG", None)

if API_TOKEN is not None and API_URL is not None:
    AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)
else:
    AUTH = None

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

    @app.route("/")
    def hello_world(**kwargs):
        return "Hello World" 

    @app.route("/oauth_status/")
    def oauth_status(**kwargs):
        token = session.get("token")
        if token:
            hub_user = AUTH.user_for_token(token)
            LOG.debug(f"Auth hub user {hub_user}")
            return "OK", 202
        else:
            hub_user = None
            LOG.debug("Hub user unauthorized")
            return "Unauthorized", 401
        
    
    @app.route("/oauth_start/")
    def oauth_start(**kwargs):
        state = AUTH.generate_state(next_url=request.path)
        LOG.info(f"Redirecting to login url {AUTH.login_url}")
        response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
        response.set_cookie(AUTH.state_cookie_name, state)
        return response

    @app.route("/oauth_callback/")
    def oauth_callback(**kwargs):
        code = request.args.get("code", None)
        if code is None:
            return "Forbidden", 403

        arg_state = request.args.get("state", None)
        cookie_state = request.cookies.get(AUTH.state_cookie_name)
        if arg_state is None or arg_state != cookie_state:
            return "Forbidden", 403

        session["token"] = AUTH.token_for_code(code)

        next_url = JUPYTERHUB_SERVICE_PREFIX
        LOG.info(f"OAuth Callback redirecting to {JUPYTERHUB_SERVICE_PREFIX}")
        response = make_response(redirect(next_url))
        return response

    return app
