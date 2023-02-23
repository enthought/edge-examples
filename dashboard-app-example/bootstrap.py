# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Bootstrap file for the dashboard example.
"""

import subprocess

ENV_NAME = "edge-dash-dev"

EDM_DEPS = [
    "click",
    "requests",
    "flask>2",
]

PIP_DEPS = [
    "jupyterhub==2.2.2",
    "sqlalchemy<2",
    "configurable-http-proxy",
    "dockerspawner",
    "Flask-Session",
]


def bootstrap():
    """Create and populate dev env"""

    print("Creating EDM Python environment...")
    cmd = ["edm", "envs", "create", ENV_NAME, "--version", "3.8", "--force"]
    subprocess.run(cmd, check=True)

    print("Installing EDM dependencies...")
    cmd = ["edm", "install", "-e", ENV_NAME, "-y"] + EDM_DEPS
    subprocess.run(cmd, check=True)

    print("Installing pip dependencies...")
    cmd = ["edm", "run", "-e", ENV_NAME, "--", "pip", "install"] + PIP_DEPS
    subprocess.run(cmd, check=True)

    print("Bootstrap complete.")
    print(f'To use your new dev environment, run "edm shell -e {ENV_NAME}"')


if __name__ == "__main__":
    bootstrap()
