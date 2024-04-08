# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Example for using Plotly Dash with Edge.
"""

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


def get_edge_session():
    """Helper function to get an EdgeSession object.

    EdgeSession will auto-load environment variables, including the API token,
    location of the Edge server, etc. Please note:

    1. In production, they are set by Edge itself; you don't have to do anything.
    2. In testing, you can set values in "dev_settings.json"

    Returns an EdgeSession object if one can be constructed, or None if the
    required information is missing.
    """

    def is_set(name):
        return name in os.environ

    if (
        is_set("EDGE_API_SERVICE_URL")
        and is_set("EDGE_API_ORG")
        and (is_set("EDGE_API_TOKEN") or is_set("JUPYTERHUB_API_TOKEN"))
    ):
        return EdgeSession()

    return None


# Note: in development, you should run "dash_app" (as in the __main__ block at
# the bottom of this file), but in your Dockerfile, gunicorn should point at
# "flask_app" instead.
flask_app = Flask(__name__)

dash_app = Dash(server=flask_app)


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
)

edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    greeting = f"Logged in as {whoami.user_name}"
else:
    greeting = "No EdgeSession available.  See the README."

dash_app.layout = html.Div(
    [
        html.H1(
            children="Population by country",
            style={"textAlign": "center"},
        ),
        html.Div(children=greeting, style={"paddingBottom": "20px"}),
        dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
        dcc.Graph(id="graph-content"),
    ]
)


# All callback functions for your UI components go here.
# For example, following is the callback for UI components in the previous
# function.
@dash_app.callback(
    Output("graph-content", "figure"), Input("dropdown-selection", "value")
)
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x="year", y="pop")


# Run the app
if __name__ == "__main__":
    dash_app.run_server(debug=True)
