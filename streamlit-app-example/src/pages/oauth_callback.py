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
from jupyterhub.services.auth import HubOAuth
from streamlit_extras.switch_page_button import switch_page

LOG = logging.getLogger(__name__)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# When run from Edge, these environment variables will be provided
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
API_URL = os.environ.get("JUPYTERHUB_API_URL", "http://127.0.0.1:8081")

AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60, api_url=API_URL)


query_params = st.experimental_get_query_params()
oauth_code = query_params.get('code')
oauth_state = query_params.get('state')

# See if the token is stored in the session. This may be the case because
# streamlit continuously runs this code
token = st.session_state.get("token")
if token is not None:
    hub_user = AUTH.user_for_token(token)
    username = hub_user["name"]
    switch_page("app")
elif oauth_code is not None and oauth_state is not None:
    # Only attempt to redeem the oauth code for a token if
    # token does not exist in the session

    # Currently cannot check oauth_state because of inability to
    # persist cookies
    oauth_code = oauth_code[0]
    token = AUTH.token_for_code(oauth_code)
    st.session_state["token"] = token
    hub_user = AUTH.user_for_token(token)
    username = hub_user["name"]
    st.write(f"Logged in as {hub_user}")
    switch_page("app")