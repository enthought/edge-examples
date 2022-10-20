# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os

from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template
from flask_session import Session

from .api.auth import auth, authenticated
from .api.users import users

SESSION_SECRET_KEY_FILE = os.environ["SESSION_SECRET_KEY"]
with open(SESSION_SECRET_KEY_FILE, "r") as fp:
    SESSION_SECRET_KEY = fp.read().strip()

CLIENT_SECRET_FILE = os.environ["OAUTH_CLIENT_SECRET"]
with open(CLIENT_SECRET_FILE, "r") as fp:
    CLIENT_SECRET = fp.read().strip()

CLIENT_ID = os.environ["OAUTH_CLIENT_ID"]
REDIRECT_URI = os.environ["OAUTH_REDIRECT_URI"]
EDGE_BASE_URL = os.environ["EDGE_BASE_URL"]

OAUTH = OAuth()
OAUTH.register(
    name="edge",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url=f"{EDGE_BASE_URL}/hub/api/oauth2/token",
    access_token_params=dict(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        grant_type="authorization_code",
    ),
    authorize_url=f"{EDGE_BASE_URL}/hub/api/oauth2/authorize",
    api_base_url=f"{EDGE_BASE_URL}/hub/api/",
)


def create_app():
    app = Flask(
        __name__,
        static_url_path="",
        template_folder="frontend/templates",
        static_folder="frontend/dist",
    )
    app.session_cookie_name = "edge-external-app"
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = SESSION_SECRET_KEY
    sess = Session()
    sess.init_app(app)
    OAUTH.init_app(app)
    app.OAUTH = OAUTH.create_client("edge")

    @app.route("/health")
    def health():
        return "healthy"

    @app.route("/")
    @authenticated
    def serve():
        return render_template("index.html")

    app.register_blueprint(auth)
    app.register_blueprint(users)

    return app
