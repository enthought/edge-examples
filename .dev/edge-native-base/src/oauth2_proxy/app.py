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

from flask import Flask, jsonify, make_response, redirect, request, session
from flask_session import Session
from jupyterhub.services.auth import HubOAuth
import requests

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.DEBUG)


# When run from Edge, these environment variables will be provided
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN")
API_URL = os.environ.get("JUPYTERHUB_API_URL")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL")
JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
HAVE_JUPYTERHUB = API_TOKEN is not None


# This *must* be provided, and must be a non-empty string
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
if not SESSION_SECRET_KEY:
    msg = "Session secret ($SESSION_SECRET_KEY) was missing or blank."
    raise RuntimeError(msg)

if API_TOKEN is not None and API_URL is not None:
    AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)
else:
    AUTH = None


def create_app():
    """Creates the Flask app with routes for facilitating OAuth"""

    app = Flask(__name__)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SECRET_KEY"] = SESSION_SECRET_KEY
    sess = Session()
    sess.init_app(app)

    @app.route("/oauth_status/")
    def oauth_status():
        """Internal route for determining auth status

        Returns
        -------
        flask.Response
            A 202 status if the user has an auth session

        """
        if not HAVE_JUPYTERHUB:
            return "OK", 202
        ping_server()
        token = session.get("token")
        if token:
            hub_user = AUTH.user_for_token(token)
            LOG.debug(f"Auth hub user {hub_user}")
            return jsonify(hub_user), 202
        else:
            hub_user = None
            LOG.debug("Hub user unauthorized")
            return "Unauthorized", 401

    @app.route("/oauth_start/")
    def oauth_start():
        """Starts the OAuth flow by creating an OAuth redirect

        Returns
        -------
        flask.Response
            A 302 redirect to the JupyterHub OAuth. If the
            required environment variables for OAuth are missing,
            then a 501 error is returned
        """
        if AUTH is None:
            return "Not Implemented", 501
        state = AUTH.generate_state(next_url=request.path)
        LOG.info(f"Redirecting to login url {AUTH.login_url}")
        response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
        response.set_cookie(AUTH.state_cookie_name, state)
        return response

    @app.route("/oauth_callback/")
    def oauth_callback():
        """An OAuth Callback route

        Returns
        -------
        flask.Response
            A 401 if authorization could not be confirmed, or a 302
            redirect back to the root of the server
        """
        code = request.args.get("code", None)
        if code is None:
            return "Unauthorized", 401

        arg_state = request.args.get("state", None)
        cookie_state = request.cookies.get(AUTH.state_cookie_name)
        if arg_state is None or arg_state != cookie_state:
            return "Unauthorized", 401

        session["token"] = AUTH.token_for_code(code)

        next_url = JUPYTERHUB_SERVICE_PREFIX
        LOG.info(f"OAuth Callback redirecting to {JUPYTERHUB_SERVICE_PREFIX}")
        response = make_response(redirect(next_url))
        return response

    return app


def ping_server():
    """Send activity ping to the JupyterHub server"""

    if not HAVE_JUPYTERHUB:
        LOG.debug("Activity ping: skipped, no JupyterHub")

    last_activity = datetime.now()

    # Format this in  format that JupyterHub understands
    if last_activity.tzinfo:
        last_activity = last_activity.astimezone(timezone.utc).replace(tzinfo=None)

    last_activity = last_activity.isoformat() + "Z"
    if ACTIVITY_URL:
        try:
            response = requests.post(
                ACTIVITY_URL,
                headers={
                    "Authorization": f"token {API_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={"servers": {SERVER_NAME: {"last_activity": last_activity}}},
            )
            response.raise_for_status()
        except Exception as e:
            LOG.error(f"Activity ping: failed {e}")
        else:
            LOG.debug(f"Activity ping: succcess ({last_activity})")
