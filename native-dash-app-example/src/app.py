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
import sys
from functools import partial, wraps
from urllib.parse import unquote

import pandas as pd
import plotly.express as px
import requests
from dash import dash, dcc, html
from dash.dependencies import Input, Output
from flask import Flask, make_response, redirect, request, session
from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import isoformat

from flask_session import Session

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
APP_VERSION = os.environ.get("APP_VERSION", "native-dash-app-example")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL", None)
EDGE_API_ORG = os.environ.get("EDGE_API_ORG", None)

DASH_URL_BASE_PATHNAME = "dashboard/"

AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)

LOG.debug(f"JUPYTERHUB_SERVER_NAME {SERVER_NAME}")
LOG.debug(f"JUPYTERHUB_SERVICE_PREFIX {PREFIX}")
LOG.debug(f"JUPYTERHUB_ACTIVITY_URL {ACTIVITY_URL}")


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


def view_authenticated(view_func, **view_args):
    """Wraps the view function with authentication."""
    token = session.get("token")
    if token:
        hub_user = AUTH.user_for_token(token)
    else:
        hub_user = None

    if hub_user or session.get("redirecting") is True:
        session["redirecting"] = False
        return view_func(**view_args)
    else:
        # redirect to login url on failed auth
        # Note that we are redirecting so we don't endlessly loop authn
        session["redirecting"] = True
        state = AUTH.generate_state(next_url=request.path)
        LOG.info(f"Redirecting to login url {AUTH.login_url}")
        response = make_response(redirect(AUTH.login_url + "&state=%s" % state))
        response.set_cookie(AUTH.state_cookie_name, state)
        return response


def create_app():
    """Creates the Flask app with routes for serving the React application
    and API routes for running jobs
    """
    flask = Flask(
        __name__,
        template_folder="templates",
        static_url_path=PREFIX + "static",
    )
    flask.config["SESSION_TYPE"] = "filesystem"
    flask.config["SECRET_KEY"] = "super secret key"
    sess = Session()
    sess.init_app(flask)
    flask.jinja_env.filters["url_decode"] = lambda url: unquote(url)

    app = dash.Dash(
        __name__,
        server=flask,
        url_base_pathname=PREFIX + DASH_URL_BASE_PATHNAME,
    )

    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    )

    app.layout = html.Div(
        [
            html.H1(
                children="Population by country",
                style={"textAlign": "center"},
            ),
            dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
            dcc.Graph(id="graph-content"),
        ]
    )

    # All of your Dash UI components go in this function.
    # Your dashboard users are not able to view those UI components unless
    # they are authenticated and authorized.
    @app.callback(
        Output("page-content", "children"),
        Input("auth-check-interval", "n_intervals"),
    )
    def layout_components(n):
        # For example, the following function returns Dropdown and Div UI
        # components that display information about the Flask and Dash
        # frameworks.
        return [
            dcc.Dropdown(
                id="frameworks_dropdown",
                options=[
                    {"label": framework, "value": framework}
                    for framework in ["Dash", "Flask"]
                ],
            ),
            html.Div(id="framework_details"),
        ]

    # All callback functions for your UI components go here.
    # For example, following is the callback for UI components in the previous
    # function.
    @app.callback(
        Output("graph-content", "figure"), Input("dropdown-selection", "value")
    )
    def update_graph(value):
        dff = df[df.country == value]
        return px.line(dff, x="year", y="pop")

    # When running with ci start, preserve the trailing slash in the prefix
    # When launching from jupyterhub, strip the trailing slash in the prefix
    ROOT_PATH = PREFIX
    if SERVER_NAME is not None and len(SERVER_NAME) > 0:
        ROOT_PATH = ROOT_PATH[:-1]

    LOG.info(f"Root path at {ROOT_PATH}")

    @flask.route(ROOT_PATH)
    @track_activity
    def serve(**kwargs):
        """The main handle to serve the index page."""
        return redirect(PREFIX + DASH_URL_BASE_PATHNAME)

    @flask.route(PREFIX + "oauth_callback")
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

    # Wrap all view functions with an authentication test
    for view_func in app.server.view_functions:
        app.server.view_functions[view_func] = partial(
            view_authenticated,
            app.server.view_functions[view_func],
        )

    return app
