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


edge_session = get_edge_session()
app = Flask(__name__)


@app.get("/")
def root():
    """Example Flask route"""

    if edge_session is None:
        html = """\
        <html><body>
        <h1>Hello World!</h1>
        <p>To see more information, run this app in Edge or set up
        the "dev_settings.json" file locally.</p>
        </body></html>"""
        return render_template_string(html)

    try:
        user_name = edge_session.whoami().user_name
    except Exception as e:
        msg = "EdgeSession error!  Check the container logs for more information."
        return msg, 500

    html = """\
    <html><body>
    <h1>Hello {{ user_name }}!</h1>
    <p>
    Welcome!  You are in the "{{ edge_session.organization }}" organization.
    </p>
    <p>
    Here is a list of the files in your organization (top folder only):
    <ul>
    {% for fname in edge_session.files.list_files() %}
    <li>{{ fname }}</li>
    {% endfor %}
    </ul>
    </p>
    <p>This example is served from: "{{ example_served_from }}".</p>
    </body></html>
    """

    # See the README.md file for more info on how routes work.  You typically
    # don't need to use this value in your code; your Flask routes, etc.,
    # should be set up as though it was located at the server root.
    example_served_from = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")

    return render_template_string(
        html,
        user_name=user_name,
        edge_session=edge_session,
        example_served_from=example_served_from,
    )
