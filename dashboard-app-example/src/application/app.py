# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import logging
import os
import random
import sys
from datetime import datetime, timezone
from functools import wraps
from urllib.parse import unquote

import requests
from flask import Flask, render_template
from flask_session import Session


LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
JUPYTERHUB_API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
JUPYTERHUB_ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
JUPYTERHUB_SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")

NATIVE_APP_MODE = os.environ.get("NATIVE_APP_MODE")
APP_VERSION = os.environ.get("APP_VERSION", "dashboard-app-example")

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
        if JUPYTERHUB_ACTIVITY_URL:
            try:
                requests.post(
                    JUPYTERHUB_ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {JUPYTERHUB_API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={"servers": {JUPYTERHUB_SERVER_NAME: {"last_activity": last_activity}}},
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


def create_app():
    """Creates the Flask app with routes for serving the React application
    """
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/dist",
        static_url_path=JUPYTERHUB_SERVICE_PREFIX + "static",
    )
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SECRET_KEY"] = "super secret key"
    sess = Session()
    sess.init_app(app)
    app.jinja_env.filters["url_decode"] = lambda url: unquote(url)

    @app.route(JUPYTERHUB_SERVICE_PREFIX)
    @track_activity
    def serve(**kwargs):
        """The main handle to serve the index page."""
        hub_user = kwargs.get("hub_user", None)
        dashboard = get_dashboard(hub_user)
        return render_template(
            "index.html",
            **{
                "dashboard": dashboard,
                "url_prefix": JUPYTERHUB_SERVICE_PREFIX,
                "app_version": APP_VERSION,
            },
        )

    return app


def get_scatterplot():
    return {
        "id": "scatterplot",
        "data": [
            {
                "x": list(range(20)),
                "y": [random.random() * 10 for n in range(20)],
                "type": "scatter",
                "mode": "lines+markers",
                "marker": {"color": "red"},
            }
        ],
        "layout": {"title": "Scatter Plot"},
        "style": {"width": "400px", "height": "400px"},
    }

def get_piechart():
    return {
        "id": "piechart",
        "data": [
            {
                "values": [random.random() * 10 for n in range(3)],
                "labels": ["Group A", "Group B", "Group C"],
                "type": "pie",
            }
        ],
        "layout": {"title": "Pie Chart"},
        "style": {"width": "400px", "height": "400px"},
    }

def get_sunburst():
    return {
        "id": "sunburst",
        "data": [
            {
                "type": "sunburst",
                "labels": [
                    "Root",
                    "Child A",
                    "Child B",
                    "Leaf B",
                    "Leaf A",
                    "Child E",
                    "Leaf C",
                ],
                "parents": [
                    "",
                    "Root",
                    "Root",
                    "Child B",
                    "Child B",
                    "Root",
                    "Child A",
                ],
                "values": [10, 16, 14, 9, 12, 4, 3, 3],
                "leaf": {"opacity": 0.5},
                "marker": {"line": {"width": 1}},
            }
        ],
        "layout": {
            "title": "Sunburst Chart",
        },
        "style": {"width": "400px", "height": "400px"},
    }

def get_choropleth():
    locations = ["United States", "Switzerland", "Japan", "United Kingdom"]
    z = [random.random() * 10 for n in range(len(locations))]
    return {
        "id": "choropleth",
        "data": [
            {
                "type": "choropleth",
                "locationmode": "country names",
                "locations": locations,
                "z": z,
                "text": locations,
                "autocolorscale": True,
            }
        ],
        "layout": {
            "title": "Choropleth Map",
            "geo": {"projection": {"type": "equirectangular"}},
        },
        "style": {"width": "1220px", "height": "400px"},
    }

def get_dashboard(hub_user):
    """Get dashboard for this hub user"""
    return {
        "plots": [
            get_scatterplot(),
            get_piechart(),
            get_sunburst(),
            get_choropleth(),
        ],
        "user": hub_user,
    }