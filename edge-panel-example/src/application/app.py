# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os

import matplotlib as mpl
import numpy as np
import pandas as pd
import panel as pn
from edge.api import EdgeSession
from matplotlib.figure import Figure

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


csv_file = (
    "https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv"
)
data = pd.read_csv(csv_file, parse_dates=["date"], index_col="date")

mpl.use("agg")


def mpl_plot(avg, highlight):
    fig = Figure()
    ax = fig.add_subplot()
    avg.plot(ax=ax)
    if len(highlight):
        highlight.plot(style="o", ax=ax)
    return fig


def find_outliers(variable="Temperature", window=30, sigma=10, view_fn=mpl_plot):
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return view_fn(avg, avg[outliers])


hello = pn.pane.Markdown(
    """
    Edge Panel Example
"""
)
edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    user_name = whoami.user_name
    hello = pn.pane.Markdown(
        f"""
        Logged in as {user_name}
    """
    )

pn.extension()

window = pn.widgets.IntSlider(name="window", value=30, start=1, end=60)
sigma = pn.widgets.IntSlider(name="sigma", value=10, start=0, end=20)

interactive = pn.bind(find_outliers, window=window, sigma=sigma)

first_app = pn.Column(hello, window, sigma, interactive)

first_app.servable()
