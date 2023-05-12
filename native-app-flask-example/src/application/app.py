# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import logging
import multiprocessing as mp
import os
import sys
from datetime import datetime, timezone
from functools import wraps
from urllib.parse import unquote
from uuid import uuid4

import requests
from edge.api import EdgeSession
from flask import Flask, render_template, request
from flask_session import Session

from .opencv_model.model import detect_face

# When running flask in debug mode outside of a JupyterHub environment,
# deactivate the `authenticated` and `track_activity` decorator.
FLASK_DEBUG = int(os.environ.get("FLASK_DEBUG", 0))

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)
if FLASK_DEBUG:
    LOG.setLevel(logging.DEBUG)

# When run from Edge, these environment variables will be provided
JUPYTERHUB_SERVICE_PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL")
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME")
API_URL = os.environ.get("JUPYTERHUB_API_URL", "http://127.0.0.1:8081")
APP_VERSION = os.environ.get("APP_VERSION", "native-app-example")

NATIVE_APP_MODE = os.environ.get("NATIVE_APP_MODE")

EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL")
EDGE_API_ORG = os.environ.get("EDGE_API_ORG")
EDGE_API_TOKEN = os.environ.get("EDGE_API_TOKEN")
JUPYTERHUB_API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN")


_EDGE_SESSION = None


def get_edge_session():
    """Helper function to get an EdgeSession object

    Returns:
        An EdgeSession object, if the container environment has
        the EDGE_API_SERVICE_URL, EDGE_API_ORG and API_TOKEN
        environment variables. If these variables are not set,
        then None is returned
    """
    global _EDGE_SESSION
    if (
        _EDGE_SESSION is None
        and EDGE_API_SERVICE_URL
        and EDGE_API_ORG
        and (EDGE_API_TOKEN or JUPYTERHUB_API_TOKEN)
    ):
        _EDGE_SESSION = EdgeSession()
    return _EDGE_SESSION


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
        if ACTIVITY_URL:
            try:
                requests.post(
                    ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {JUPYTERHUB_API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={"servers": {SERVER_NAME: {"last_activity": last_activity}}},
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


def task(id: str, result_dict: dict, encoded_string: str, params: dict) -> None:
    """Run face detection and store the result"""
    result = detect_face(encoded_string, params)
    result_dict[id] = result


def create_app():
    """Creates the Flask app with routes for serving the React application
    and API routes for running jobs
    """
    mp.set_start_method("spawn")  # Starts a fresh process instead of forking.
    manager = mp.Manager()

    # Use a multiprocessing shared dictionary for aggregating job results
    RESULTS = manager.dict()

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
        edge = get_edge_session()
        user_name = None
        if edge is not None:
            whoami = edge.whoami()
            user_name = whoami.user_name
        props = {
            "url_prefix": JUPYTERHUB_SERVICE_PREFIX,
            "app_version": APP_VERSION,
        }
        if user_name is not None:
            props["user_name"] = user_name
        return render_template("index.html", **props)

    @app.route(JUPYTERHUB_SERVICE_PREFIX + "job", methods=["GET", "POST"])
    @track_activity
    def job(**kwargs):
        """A job endpoint for receiving images and returning job results"""
        if request.method == "GET":
            # Return finished task results and remove them from shared results
            ret = {}
            for taskId, value in RESULTS.items():
                if value:
                    ret[taskId] = value
                del RESULTS[taskId]
            return ret

        if request.method == "POST":
            # Spawn a face detection task and an id
            body = request.json
            id = str(uuid4())
            RESULTS[id] = None
            p = mp.Process(
                target=task, args=(id, RESULTS, body["image"], body["params"])
            )
            p.start()

            return {"id": id}

    return app
