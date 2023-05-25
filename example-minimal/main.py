"""
    Example Flask application (minimal).
"""

import os
from flask import Flask, render_template_string

from edge.api import EdgeSession, EdgeSessionError


# EdgeSession will auto-load environment variables, including the API token,
# location of the Edge server, etc. Please note:
#
# 1. In production, they are set by Edge itself.  You don't have to do anything.
# 2. In testing, you can set values in "edge_settings.json"
try:
    session = EdgeSession()
except EdgeSessionError as e:
    print("Edge session not available.  Reason: {e}")
    session = None


# You can check whether you're running inside of Edge by looking for the
# presence of this variable, which is set by JupyterHub.
running_in_edge = "JUPYTERHUB_SERVICE_NAME" in os.environ


app = Flask(__name__)


@app.get("/")
def root():
    if session is not None:
        user_name = session.whoami().user_name
    else:
        user_name = "(not available)"

    return render_template_string(
        HTML,
        user_name=user_name,
        running_in_edge=running_in_edge,
    )


HTML = """\
<html>
<body>
<h1>Hello World!</h1>
<ul>
<li>User Name: {{ user_name }}</li>
<li>Running in Edge? {{ running_in_edge }}</li>
</ul>
</body>
</html>
"""
