# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

from flask import Blueprint, session

users = Blueprint("users", __name__)


@users.route("/user")
def get_user():
    """Get the logged-in user's ID."""
    user_id = session.get("user_id")
    return {"user_id": user_id}, 200
