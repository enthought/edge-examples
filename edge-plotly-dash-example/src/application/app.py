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

import pandas as pd
import plotly.express as px
import requests
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from edge.api import EdgeSession
from flask import Flask

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

# Incorporate data
df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)


# When run from Edge, these environment variables will be provided
JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL")
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME")
API_URL = os.environ.get("JUPYTERHUB_API_URL", "http://127.0.0.1:8081")
APP_VERSION = os.environ.get("APP_VERSION", "native-app-example")

NATIVE_APP_MODE = os.environ.get("NATIVE_APP_MODE")

JUPYTERHUB_API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL")
EDGE_API_ORG = os.environ.get("EDGE_API_ORG")
EDGE_API_TOKEN = os.environ.get("EDGE_API_TOKEN")
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
        and (JUPYTERHUB_API_TOKEN or EDGE_API_TOKEN)
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
        # Format this in  format that JupyterHub understands
        if last_activity.tzinfo:
            last_activity = last_activity.astimezone(timezone.utc).replace(tzinfo=None)
        last_activity = last_activity.isoformat() + "Z"
        if ACTIVITY_URL:
            try:
                requests.post(
                    ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {JUPYTERHUB_API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={"servers": {SERVER_NAME: {"last_activity": last_activity}}},
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


server = Flask(__name__)
app = Dash(server=server, url_base_pathname=JUPYTERHUB_SERVICE_PREFIX)

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

greeting = ""
edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    greeting = f"Logged in as {whoami.user_name}"


app.layout = html.Div(
    [
        html.H1(
            children="Population by country",
            style={"textAlign": "center"},
        ),
        dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
        dcc.Graph(id="graph-content"),
        html.Div(children=greeting),
    ]
)


# All callback functions for your UI components go here.
# For example, following is the callback for UI components in the previous
# function.
@app.callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
@track_activity
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x="year", y="pop")


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
