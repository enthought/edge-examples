# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    This is the "ci" module for the Core Panel example.
"""

import click
import os.path as op
import subprocess
import sys
import os
import json

SRC_ROOT = op.abspath(op.join(op.dirname(__file__), ".."))

# Docker image will be tagged "IMAGE:VERSION"
IMAGE = "quay.io/enthought/edge-panel-core"
VERSION = "1.1.0"

# These will go into the built Docker image.  You may wish to modify this
# minimal example to pin the dependencies, or use a bundle file to define them.
APP_DEPENDENCIES = [
    "enthought_edge>=2.6.0",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "panel",
    "numpy",
    "pandas",
    "matplotlib",
]

# This will be used when running locally ("run" command).
# We just use the last component of the full image URL.
CONTAINER_NAME = IMAGE.split("/")[-1]


@click.group()
def cli():
    """Group for Click commands"""
    pass


@cli.command()
@click.option("--rebuild-zbundle", default=False, is_flag=True)
def build(rebuild_zbundle):
    """Build the Docker image"""

    # First, we build a "zbundle" which contains all the eggs needed to
    # build the environment within the Docker image.
    fname = "app_environment.zbundle"
    if rebuild_zbundle or not op.exists(op.join(SRC_ROOT, fname)):
        cmd = [
            "edm",
            "bundle",
            "generate",
            "-i",
            "--version",
            "3.8",
            "--platform",
            "rh7-x86_64",
            "-m",
            "2.0",
            "-f",
            fname,
        ] + APP_DEPENDENCIES
        subprocess.run(cmd, check=True, cwd=SRC_ROOT)

    # Second, we run Docker.  The Dockerfile will copy the zbundle into
    # a temp folder and install it.
    cmd = ["docker", "build", "-t", f"{IMAGE}:{VERSION}", "."]
    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
def run():
    """Run the Docker image for testing"""

    # Get values from the dev settings file (API tokens for testing, etc.)
    envs = _load_dev_settings()

    cmd = ["docker", "run", "--rm", "-p", "9000:9000", "--name", CONTAINER_NAME]
    for key, value in envs.items():
        cmd += ["--env", f"{key}={value}"]
    cmd += ["--env", "HOST_ADDRESS=0.0.0.0"]
    cmd += [f"{IMAGE}:{VERSION}"]

    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
def publish():
    """Publish the Docker image for use with Edge"""
    cmd = ["docker", "push", f"{IMAGE}:{VERSION}"]
    subprocess.run(cmd, check=True)


def _load_dev_settings():
    """Load dev_settings.json file.

    Returns a dict with "EDGE_*" key/value pairs, or an empty dict if the
    file doesn't exist.  Any other keys are filtered out.
    """
    fpath = op.join(SRC_ROOT, "dev_settings.json")
    if not op.exists(fpath):
        return {}
    with open(fpath, "r") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if k.startswith("EDGE_")}


if __name__ == "__main__":
    cli()
