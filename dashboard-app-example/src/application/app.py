# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import datetime
import logging
import os
import random
import sys
from functools import wraps
from urllib.parse import unquote

import requests
from flask import Flask, make_response, redirect, render_template, request, session
from flask_session import Session
from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import isoformat

# Flag to deactivate the `authenticated` and `track_activity` decorator.
# It is used to develop the app outside of JupyterHub environment.
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

PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
APP_VERSION = os.environ.get("APP_VERSION", "dashboard-app-example")


AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60)


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
            response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
            response.set_cookie(AUTH.state_cookie_name, state)
            return response

    return decorated


def create_app():
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
        hub_user = kwargs.get("hub_user", None)
        dashboard = get_dashboard(hub_user)
        return render_template(
            "index.html",
            **{
                "dashboard": dashboard,
                "url_prefix": PREFIX,
                "app_version": APP_VERSION,
            },
        )

    def get_scatterplot():
        return {
            "id": "scatterplot",
            "data": [
                {
                    "x": list(range(20)),
                    "y": [random.random() * 10 for n in range(20)],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "marker": {"color": "red"},
                }
            ],
            "layout": {"title": "Scatter Plot"},
            "style": {"width": "400px", "height": "400px"},
        }

    def get_piechart():
        return {
            "id": "piechart",
            "data": [
                {
                    "values": [random.random() * 10 for n in range(3)],
                    "labels": ["Group A", "Group B", "Group C"],
                    "type": "pie",
                }
            ],
            "layout": {"title": "Pie Chart"},
            "style": {"width": "400px", "height": "400px"},
        }

    def get_sunburst():
        return {
            "id": "sunburst",
            "data": [
                {
                    "type": "sunburst",
                    "labels": [
                        "Root",
                        "Child A",
                        "Child B",
                        "Leaf B",
                        "Leaf A",
                        "Child E",
                        "Leaf C",
                    ],
                    "parents": [
                        "",
                        "Root",
                        "Root",
                        "Child B",
                        "Child B",
                        "Root",
                        "Child A",
                    ],
                    "values": [10, 16, 14, 9, 12, 4, 3, 3],
                    "leaf": {"opacity": 0.5},
                    "marker": {"line": {"width": 1}},
                }
            ],
            "layout": {
                "title": "Sunburst Chart",
            },
            "style": {"width": "400px", "height": "400px"},
        }

    def get_choropleth():
        locations = ["United States", "Switzerland", "Japan", "United Kingdom"]
        z = [random.random() * 10 for n in range(len(locations))]
        return {
            "id": "choropleth",
            "data": [
                {
                    "type": "choropleth",
                    "locationmode": "country names",
                    "locations": locations,
                    "z": z,
                    "text": locations,
                    "autocolorscale": True,
                }
            ],
            "layout": {
                "title": "Choropleth Map",
                "geo": {"projection": {"type": "equirectangular"}},
            },
            "style": {"width": "1220px", "height": "400px"},
        }

    def get_dashboard(hub_user):
        """Get dashboard for this hub user"""
        return {
            "plots": [
                get_scatterplot(),
                get_piechart(),
                get_sunburst(),
                get_choropleth(),
            ],
            "user": hub_user,
        }

    @app.route(PREFIX + "oauth_callback")
    def oauth_callback():
        """The OAuth callback handle, this handle is required for the
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
        response = make_response(redirect(next_url))
        return response

    return app
