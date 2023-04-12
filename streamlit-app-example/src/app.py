# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is 

# Streamlit Example App:
# https://docs.streamlit.io/library/get-started/create-an-app

import logging
import os
import streamlit as st
import pandas as pd
import numpy as np
from jupyterhub.services.auth import HubOAuth

LOG = logging.getLogger(__name__)


# When run from Edge, these environment variables will be provided
PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")
JUPYTERHUB_SERVICE_URL = os.environ.get("JUPYTERHUB_SERVICE_URL")
JUPYTERHUB_OAUTH_SCOPES = os.environ.get("JUPYTERHUB_OAUTH_SCOPES")
API_URL = os.environ.get("JUPYTERHUB_API_URL", "http://127.0.0.1:8081")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL", None)
EDGE_API_ORG = os.environ.get("EDGE_API_ORG", None)

AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)


if 'token' in st.session_state:
    hub_user = AUTH.user_for_token(st.session_state['token'])
else:
    hub_user = None
    state = AUTH.generate_state(next_url=JUPYTERHUB_SERVICE_URL)
    redirect_url = f"{AUTH.login_url}&state={state}"
    # Use a meta tag to perform an automatic redirect
    st.markdown(
        f'''
        <meta http-equiv="refresh" content="0;URL='{redirect_url}'" />
        ''',
        unsafe_allow_html=True
    )


st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)