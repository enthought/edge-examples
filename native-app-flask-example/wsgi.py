# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

""" Helper module for Gunicorn. """

import os
from urllib.parse import urlparse

import gunicorn.app.base

from .app import create_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":

    service_url = os.environ.get("JUPYTERHUB_SERVICE_URL", None)
    port = 8888
    host = "0.0.0.0"
    if service_url:
        url = urlparse(service_url)
        port = url.port
        host = url.hostname
    options = {"bind": f"{host}:{port}", "workers": 1, "threads": 1}
    application = create_app()
    StandaloneApplication(application, options).run()
