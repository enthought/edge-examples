# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os
import secrets
import sys
import threading
from queue import Empty, Queue
from urllib.parse import unquote
from uuid import uuid4

from edge.api import EdgeSession
from flask import Flask, render_template, request
from flask_session import Session

from .opencv_model.model import detect_face

PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")


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


# Used to determine user name; could also be used to store the result in
# the Edge file system.
EDGE_SESSION = get_edge_session()

# This will be used to hold the compute jobs.
RESULTS = Queue()


def task(task_id, encoded_string, params):
    """Compute task result and store it in a global when done."""
    RESULTS.put((task_id, detect_face(encoded_string, params)))


app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/dist",
    static_url_path=PREFIX + "static",
)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = secrets.token_hex()
sess = Session()
sess.init_app(app)
app.jinja_env.filters["url_decode"] = lambda url: unquote(url)


@app.route(PREFIX)
def serve():
    """The main handle to serve the index page."""

    if EDGE_SESSION is not None:
        user_name = EDGE_SESSION.whoami().user_name
    else:
        user_name = "(user name not available)"

    return render_template("index.html", url_prefix=PREFIX, user_name=user_name)


@app.route(PREFIX + "job", methods=["GET", "POST"])
def job():
    """A job endpoint for receiving images and returning job results"""

    if request.method == "GET":
        # De-queue and return any finished jobs

        ret = {}
        while True:
            try:
                task_id, result = RESULTS.get(block=False)
                RESULTS.task_done()
                ret[task_id] = result
            except Empty:
                break
        return ret

    if request.method == "POST":
        # Spawn a face detection task and an id

        body = request.json
        task_id = str(uuid4())
        t = threading.Thread(target=task, args=(task_id, body["image"], body["params"]))
        t.start()

        return {"id": task_id}
