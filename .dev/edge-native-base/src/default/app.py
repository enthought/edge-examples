# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Default application for edge-native-base.
"""

import os
from flask import Flask, render_template_string

PREFIX = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/")

app = Flask(__name__)


@app.get(PREFIX)
def root():
    """Flask route for home page"""

    html = """\
    <html><body>
    This is the default edge-native-base application. Please replace
    startup-script.sh with your application launcher.
    </body></html>"""

    return render_template_string(html)
