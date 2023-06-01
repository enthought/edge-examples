# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Settings file for "edge-native-base".
"""

import os
import subprocess

from ci.builders import ContainerBuilder, DevBuilder, PreflightBuilder

APP_NAME = "Edge Native Base"
IMAGE_NAME = "quay.io/enthought/edge-native-base"
IMAGE_TAG = "1.1.0"
CONTAINER_NAME = "edge-native-base"
ENV_NAME = "edge-native-base"

# Dependencies for bootstrap.py development environment
EDM_DEPS = [
    "click",
    "flask>2",
    "enthought_edge>=2.6.0",
    "pytest",
    "requests",
    "gunicorn",
]
PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "dockerspawner",
]

# EDM dependencies that will be packaged into the Docker container
BUNDLE_PACKAGES = [
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "click",
    "requests",
]
BUNDLE_NAME = "app_environment.zbundle"
MODULE_DIR = os.path.join(os.path.dirname(__file__))
CI_DIR = os.path.join(MODULE_DIR, "ci")
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
LINT_ENV_NAME = f"lint-{ENV_NAME}"
SRC_DIR = os.path.join(MODULE_DIR, "src")


class NativeBaseDevBuilder(DevBuilder):
    def run(self):
        env = os.environ.copy()
        env.update(self.context.env)
        cmd = ["gunicorn", "app:app", "-b", "127.0.0.1:9000"]
        app_dir = os.path.join(self.context.src_dir, "default")
        subprocess.run(cmd, check=True, env=env, cwd=app_dir)

    def test(self):
        pass


DEV_BUILDER_CLS = NativeBaseDevBuilder
CONTAINER_BUILDER_CLS = ContainerBuilder
PREFLIGHT_BUILDER_CLS = PreflightBuilder
