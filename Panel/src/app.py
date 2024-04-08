# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Example Panel application for Edge.
"""
import os

import matplotlib as mpl
import numpy as np
import pandas as pd
import panel as pn

from edge.api import EdgeSession
from matplotlib.figure import Figure


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


hello = pn.pane.Markdown("Edge Panel Example")

edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    user_name = whoami.user_name
    greeting = pn.pane.Markdown(f"Logged in as {user_name}")
else:
    greeting = pn.pane.Markdown(f"No EdgeSession available; see the README.")


pn.extension()

window = pn.widgets.IntSlider(name="window", value=30, start=1, end=60)
sigma = pn.widgets.IntSlider(name="sigma", value=10, start=0, end=20)

interactive = pn.bind(find_outliers, window=window, sigma=sigma)

first_app = pn.Column(hello, greeting, window, sigma, interactive)

first_app.servable()
