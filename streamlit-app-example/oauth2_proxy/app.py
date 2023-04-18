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

from flask import Flask, make_response, redirect, request, session, jsonify
from flask_session import Session
from jupyterhub.services.auth import HubOAuth


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
JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "super secret key")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL", None)
EDGE_API_ORG = os.environ.get("EDGE_API_ORG", None)

if API_TOKEN is not None and API_URL is not None:
    AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)
else:
    AUTH = None

def create_app():
    """Creates the Flask app with routes for facilitating OAuth
    """
    app = Flask(
        __name__,
    )
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
        token = session.get("token")
        if token:
            hub_user = AUTH.user_for_token(token)
            LOG.debug(f"Auth hub user {hub_user}")
            return "OK", 202
        else:
            hub_user = None
            LOG.debug("Hub user unauthorized")
            return "Unauthorized", 401

    @app.route("/edge_auth/")
    def edge_auth():
        """Service route for returning EdgeSession settings
        
        Returns
        -------
        flask.JsonResponse
            A dictionary that can be passed to edge.api.EdgeSession
            as kwargs
        """
        token = session.get("token")
        if token is None:
            return "Unauthorized", 401
        return jsonify({
            "api_token": token,
            "service_url": EDGE_API_SERVICE_URL,
            "organization": EDGE_API_ORG
        })
    
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
