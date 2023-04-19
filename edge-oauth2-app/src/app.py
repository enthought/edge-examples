# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import sys

from flask import Flask
import logging
import requests

LOG = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        """The main handle to serve the index page."""
        return "Hello World"

    return app
