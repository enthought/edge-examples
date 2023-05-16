# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Settings file for the "panel" example.
"""

import os
import subprocess

from ci.builders import ContainerBuilder, DevBuilder, PreflightBuilder


### APPLICATION SETTINGS AND DEPENDENCIES #####################################

APP_NAME = "Edge Panel Example"
IMAGE_NAME = "quay.io/enthought/edge-panel-example"
IMAGE_TAG = "1.0.0"
CONTAINER_NAME = "example-panel"
ENV_NAME = "example-panel"

# Dependencies for bootstrap.py development environment
EDM_DEPS = [
    "click",
    "enthought_edge>=2.6.0",
    "pytest",
    "requests",
    "panel",
    "pandas",
    "matplotlib",
]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
]

# EDM dependencies that will be packaged into the Docker container
BUNDLE_PACKAGES = [
    "enthought_edge>=2.6.0",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "click",
    "panel",
    "numpy",
    "pandas",
    "matplotlib",
]

###############################################################################


BUNDLE_NAME = "app_environment.zbundle"
MODULE_DIR = os.path.join(os.path.dirname(__file__))
CI_DIR = os.path.join(MODULE_DIR, "ci")
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
LINT_ENV_NAME = f"lint-{ENV_NAME}"
SRC_DIR = os.path.join(MODULE_DIR, "src")


class PanelDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = [
            "panel",
            "serve",
            "application/app.py",
            "--port=9000",
            "--allow-websocket-origin=*",
        ]
        subprocess.run(cmd, check=True, env=env, cwd=self.context.src_dir)

    def test(self):
        pass


class PanelPreflightBuilder(PreflightBuilder):
    @property
    def _test_path(self):
        return "preflight/test_panel_preflight.py"


DEV_BUILDER_CLS = PanelDevBuilder
CONTAINER_BUILDER_CLS = ContainerBuilder
PREFLIGHT_BUILDER_CLS = PanelPreflightBuilder
