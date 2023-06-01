# Enthought product code (except portions from the official Streamlit example)
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

# Adapted from Streamlit Example App:
# https://docs.streamlit.io/library/get-started/create-an-app

"""
    Example Streamlit application, adapted for Edge
"""

import os

import numpy as np
import pandas as pd
import streamlit as st

from edge.api import EdgeSession


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


st.set_page_config(page_title="", initial_sidebar_state="collapsed")
st.title("Uber pickups in NYC")

edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    user_name = whoami.user_name
    st.write(f"Logged in as {user_name}")
else:
    st.write(f"No Edge Session data available; see the README.")
    st.write(
        f"When running outside of Edge, you'll need to provide 'dev_settings.json'."
    )

DATE_COLUMN = "date/time"
DATA_URL = (
    "https://s3-us-west-2.amazonaws.com/"
    "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)


def lowercase(value):
    return str(value).lower()


@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


data_load_state = st.text("Loading data...")
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(data)

st.subheader("Number of pickups by hour")
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider("hour", 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader("Map of all pickups at %s:00" % hour_to_filter)
st.map(filtered_data)
