# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import datetime
import multiprocessing as mp
import os
import random
from functools import wraps
from uuid import uuid4

import requests
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session
)
from flask_session import Session
from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import isoformat


from .opencv_model.model import detect_face

# Flag to deactivate the `authenticated` and `track_activity` decorator.
# It is used to develop the app outside of JupyterHub environment.
DEV_MODE = int(os.environ.get("DEV_MODE", 0))

PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")
API_TOKEN = os.environ.get("JUPYTERHUB_API_TOKEN", "")
ACTIVITY_URL = os.environ.get("JUPYTERHUB_ACTIVITY_URL", None)
SERVER_NAME = os.environ.get("JUPYTERHUB_SERVER_NAME", "")


AUTH = HubOAuth(api_token=API_TOKEN, cache_max_age=60)


def track_activity(f):
    """Decorator for reporting server activities with the Hub"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if DEV_MODE == 1:
            return f(*args, **kwargs)
        last_activity = isoformat(datetime.datetime.now())
        if ACTIVITY_URL:
            try:
                requests.post(
                    ACTIVITY_URL,
                    headers={
                        "Authorization": f"token {API_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "servers": {
                            SERVER_NAME: {"last_activity": last_activity}
                        }
                    },
                )
            except Exception:
                pass
        return f(*args, **kwargs)

    return decorated


def authenticated(f):
    """Decorator for authenticating with the Hub via OAuth"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if DEV_MODE == 1:
            return f(*args, **kwargs)
        token = session.get("token")
        if token:
            hub_user = AUTH.user_for_token(token)
        else:
            hub_user = None

        if hub_user:
            return f(*args, hub_user=hub_user, **kwargs)
        else:
            # redirect to login url on failed auth
            state = AUTH.generate_state(next_url=request.path)
            response = make_response(
                redirect(AUTH.login_url + "&state=%s" % state)
            )
            response.set_cookie(AUTH.state_cookie_name, state)
            return response

    return decorated


def task(id: str, result_dict: dict,
         encoded_string: str, params: dict) -> None:
    result = detect_face(encoded_string, params)
    result_dict[id] = result


def create_app():

    mp.set_start_method("spawn")  # Starts a fresh process instead of forking.
    manager = mp.Manager()

    RESULTS = manager.dict()

    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/dist",
        static_url_path=PREFIX + "static",
    )
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = "super secret key"
    sess = Session()
    sess.init_app(app)

    @app.route(PREFIX)
    @track_activity
    @authenticated
    def serve(**kwargs):
        """The main handle to serve the index page."""
        hub_user = kwargs.get("hub_user", None)
        dashboard = get_dashboard(hub_user)
        return render_template(
            "index.html", **{"dashboard": dashboard, "url_prefix": PREFIX}
        )

    def get_scatterplot(id):
        return {
            "id": id,
            "data": [{
                "x": list(range(20)),
                "y": [random.random() * 10 for n in range(20)],
                "type": "scatter",
                "mode": "lines+markers",
                "marker": {"color": "red"},
            }],
            "layout": {
                "title": "Scatter Plot"
            },
            "style": {
                "width": "400px",
                "height": "400px"
            }
        }

    def get_piechart(id):
        return {
            "id": id,
            "data": [{
                "values": [23, 26, 51],
                "labels": ['Group A', 'Group B', 'Group C'],
                "type": "pie"
            }],
            "layout": {
                "title": "Pie Chart"
            },
            "style": {
                "width": "400px",
                "height": "400px"
            }
        }
    

    def get_sunburst(id):
        return {
            "id": id,
            "data": [{
                "type": "sunburst",
                "labels": ["Root", "Child A", "Child B", "Leaf B", "Leaf A",  "Child E", "Leaf C"],
                "parents": ["", "Root", "Root", "Child B", "Child B", "Root", "Child A" ],
                "values":  [10, 16, 14, 9, 12, 4, 3, 3],
                "leaf": {"opacity": 0.5},
                "marker": {"line": {"width": 1}},
            }],
            "layout": {
                "title": "Sunburst Chart",
            },
            "style": {
                "width": "450px",
                "height": "450px"
            }
        }

    def get_dashboard(hub_user):
        """Get dashboard for this hub user"""
        return {
            "plots": [
                get_scatterplot("scatter1"),
                get_piechart("pie1"),
                get_sunburst("sunburst1")
            ],
           "user": hub_user
        }

    @app.route(PREFIX + "job", methods=["GET", "POST"])
    @track_activity
    @authenticated
    def job(**kwargs):
        if request.method == "GET":
            ret = {}
            for taskId, value in RESULTS.items():
                if value:
                    ret[taskId] = value
                del RESULTS[taskId]
            return ret

        if request.method == "POST":
            body = request.json
            id = str(uuid4())
            RESULTS[id] = None
            p = mp.Process(
                target=task, args=(id, RESULTS, body["image"], body["params"])
            )
            p.start()

            return {"id": id}

    @app.route(PREFIX + "oauth_callback")
    def oauth_callback():
        """The OAuth callback handle, this handle is required for the
        authentication process with Hub.
        """

        code = request.args.get("code", None)
        if code is None:
            return "Forbidden", 403

        arg_state = request.args.get("state", None)
        cookie_state = request.cookies.get(AUTH.state_cookie_name)
        if arg_state is None or arg_state != cookie_state:
            return "Forbidden", 403

        session["token"] = AUTH.token_for_code(code)

        next_url = AUTH.get_next_url(cookie_state) or PREFIX
        response = make_response(redirect(next_url))
        return response

    return app
