# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

# Streamlit Example App:
# https://docs.streamlit.io/library/get-started/create-an-app

import logging
import os

import numpy as np
import pandas as pd
import streamlit as st
from edge.api import EdgeSession

LOG = logging.getLogger(__name__)

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


st.set_page_config(page_title="", initial_sidebar_state="collapsed")

st.title("Uber pickups in NYC")

edge = get_edge_session()
if edge is not None:
    whoami = edge.whoami()
    user_name = whoami.user_name
    st.write(f"Logged in as {user_name}")

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
