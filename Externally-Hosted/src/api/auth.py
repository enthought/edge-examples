# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import logging
import os
from functools import wraps

from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, request, session, url_for

FLASK_DEBUG = int(os.environ.get("FLASK_DEBUG", 0))
LOG = logging.getLogger(__name__)


auth = Blueprint("auth", __name__)


def authenticated(f):
    """Verify we have information on the user's ID"""

    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None or FLASK_DEBUG:
            # We have a valid, logged-in user
            return f(*args, **kwargs)
        else:
            # Redirect to our /login endpoint
            return redirect("login")

    return decorated


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Login endpoint to serve the login page and process login requests."""
    if request.method == "GET":
        user_id = session.get("user_id")
        if user_id is None or FLASK_DEBUG:
            return render_template("login.html")
        else:
            return redirect("/")

    redirect_uri = url_for("auth.authorize", _external=True)
    # Redirect to OAuth provider (Edge), then back
    # to our 'redirect_uri' callback to handle the response
    return app.OAUTH.authorize_redirect(redirect_uri)


@auth.route("/authorize")
def authorize():
    """Callback to handle the reponse from the OAuth provider.

    In this callback, we exchange the authorization code returned from the
    initial request for an access token.

    With the access token in hand, we query the provider for the user
    information and save the user ID in our session. This user ID will be used
    throught the application to identify the signed-in user.
    """
    try:
        app.OAUTH.authorize_access_token()
    except OAuthError as e:
        LOG.error(f"Error getting access token: {str(e)}")
        # redirect to an error page
        return "Error logging in", 401

    # Get the user information from the provider
    response = app.OAUTH.get("user")
    user_id = response.json().get("name")

    # IMPORTANT: Additional validation should occur here to verify that
    # the user_id provided by Edge has access to your application.
    if not user_is_authorized(user_id):
        return "User does not have permission to access this app", 403

    # Save the user ID to our Flask session to be referenced later throughout
    # our application
    session["user_id"] = user_id

    return redirect("/")


@auth.route("/logout", methods=["POST"])
def logout():
    """Logout endpoint."""
    # Remove the user id from our session
    session.pop("user_id", None)
    return redirect("login")


def user_is_authorized(user_id):
    """Stub function for checking if a particular user ID is allowed access.

    You can trust that the user_id is genuine; Edge guarantees this as part
    of the login process.  As the app developer, you're responsible for also
    deciding whether to grant a particular user access.

    One example of a way to perform an authorization check would be to maintain
    a database table, or even a configuration file, with a list of allowed
    users.
    """
    return True
