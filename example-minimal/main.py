# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Example Flask application (minimal).
"""

import os
from flask import Flask, render_template_string

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


session = get_edge_session()
app = Flask(__name__)


@app.get("/")
def root():
    if session is not None:
        user_name = session.whoami().user_name
    else:
        user_name = "(Not available; please run in Edge or set up 'dev_settings.json')"

    html = """\
    <html><body>
    <h1>Hello World!</h1>
    <p>
    <li>User Name: {{ user_name }}</li>
    </ul>
    </body></html>
    """

    return render_template_string(html, user_name=user_name)
