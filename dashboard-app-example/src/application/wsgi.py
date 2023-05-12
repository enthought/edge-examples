# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

""" Helper module for Gunicorn. """

import os

import gunicorn.app.base

from .app import create_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
    A gunicorn custom application

    https://docs.gunicorn.org/en/stable/custom.html
    """

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
    """Application main, which looks for JUPYTERHUB_SERVICE_URL provided
    by Edge and binds Flask to the provided endpoint
    """
    service_url = os.environ.get("JUPYTERHUB_SERVICE_URL", None)
    port = 9000
    host = "0.0.0.0"
    options = {"bind": f"{host}:{port}", "workers": 1, "threads": 1}
    application = create_app()
    StandaloneApplication(application, options).run()
