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
from edge.api import EdgeSession

from .opencv_model.model import detect_face

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

AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)

LOG.debug(f"JUPYTERHUB_SERVER_NAME {SERVER_NAME}")
LOG.debug(f"JUPYTERHUB_SERVICE_PREFIX {PREFIX}")
LOG.debug(f"JUPYTERHUB_ACTIVITY_URL {ACTIVITY_URL}")

if EDGE_API_SERVICE_URL and EDGE_API_ORG and API_TOKEN:
    edge = EdgeSession(
        service_url=EDGE_API_SERVICE_URL,
        organization=EDGE_API_ORG,
        version_num="1",
        api_token=API_TOKEN
    )
    LOG.info(f"Edge initialized")


def track_activity(f):
    """Decorator for reporting server activities with the Hub"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if FLASK_DEBUG == 1:
            return f(*args, **kwargs)
        last_activity = isoformat(datetime.datetime.now())
        if ACTIVITY_URL:
            try:
                requests.post(
                    ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={"servers": {SERVER_NAME: {"last_activity": last_activity}}},
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


def authenticated(f):
    """Decorator for authenticating with the Hub via OAuth"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if FLASK_DEBUG == 1:
            return f(*args, **kwargs)
        token = session.get("token")
        if token:
            hub_user = AUTH.user_for_token(token)
        else:
            hub_user = None

        if hub_user:
            return f(*args, hub_user=hub_user, **kwargs)
        else:
            # redirect to login url on failed auth
            state = AUTH.generate_state(next_url=request.path)
            LOG.info(f"Redirecting to login url {AUTH.login_url}")
            response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
            response.set_cookie(AUTH.state_cookie_name, state)
            return response

    return decorated


def task(id: str, result_dict: dict, encoded_string: str, params: dict) -> None:
    """Run face detection and store the result"""
    result = detect_face(encoded_string, params)
    result_dict[id] = result


def create_app():
    """Creates the Flask app with routes for serving the React application
    and API routes for running jobs
    """
    mp.set_start_method("spawn")  # Starts a fresh process instead of forking.
    manager = mp.Manager()

    # Use a multiprocessing shared dictionary for aggregating job results
    RESULTS = manager.dict()

    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/dist",
        static_url_path=PREFIX + "static",
    )
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SECRET_KEY"] = "super secret key"
    sess = Session()
    sess.init_app(app)
    app.jinja_env.filters["url_decode"] = lambda url: unquote(url)

    # When running with ci start, preserve the trailing slash in the prefix
    # When launching from jupyterhub, strip the trailing slash in the prefix
    ROOT_PATH = PREFIX
    if SERVER_NAME is not None and len(SERVER_NAME) > 0:
        ROOT_PATH = ROOT_PATH[:-1]

    LOG.info(f"Root path at {ROOT_PATH}")

    @app.route(ROOT_PATH)
    @track_activity
    @authenticated
    def serve(**kwargs):
        """The main handle to serve the index page."""
        hub_user = kwargs.get("hub_user", {"name": "No user"})
        return render_template(
            "index.html",
            **{
                "user": hub_user["name"],
                "url_prefix": PREFIX,
                "app_version": APP_VERSION,
            },
        )

    @app.route(PREFIX + "job", methods=["GET", "POST"])
    @track_activity
    @authenticated
    def job(**kwargs):
        """A job endpoint for receiving images and returning job results"""
        if request.method == "GET":
            # Return finished task results and remove them from shared results
            ret = {}
            for taskId, value in RESULTS.items():
                if value:
                    ret[taskId] = value
                del RESULTS[taskId]
            return ret

        if request.method == "POST":
            # Spawn a face detection task and an id
            body = request.json
            id = str(uuid4())
            RESULTS[id] = None
            p = mp.Process(
                target=task, args=(id, RESULTS, body["image"], body["params"])
            )
            p.start()

            return {"id": id}

    @app.route(PREFIX + "oauth_callback")
    def oauth_callback():
        """The OAuth callback handler, this handler is required for the
        authentication process with Hub.
        """

        code = request.args.get("code", None)
        if code is None:
            return "Forbidden", 403

        arg_state = request.args.get("state", None)
        cookie_state = request.cookies.get(AUTH.state_cookie_name)
        if arg_state is None or arg_state != cookie_state:
            return "Forbidden", 403

        session["token"] = AUTH.token_for_code(code)

        next_url = AUTH.get_next_url(cookie_state) or PREFIX
        LOG.info(f"OAuth Callback redirecting to {next_url}")
        response = make_response(redirect(next_url))
        return response

    return app
