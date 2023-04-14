# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os
import shutil
import subprocess

import click

DASH_EXAMPLE_IMAGE = "quay.io/enthought/native-dash-app-demo"
DASH_EXAMPLE_CONTAINER = "native-dash-app-flask"

CI_DIR = os.path.dirname(__file__)
MODULE_DIR = os.path.join(CI_DIR, "..")
SRC_DIR = os.path.join(MODULE_DIR, "src")

BUNDLE_NAME = "app_environment.zbundle"
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
BUNDLE_PATH = os.path.join(ARTIFACT_DIR, BUNDLE_NAME)

BUNDLE_PACKAGES = [
    "enthought_edge",
    "appdirs",
    "click",
    "dash",
    "flask>2",
    "gunicorn",
    "opencv_python",
    "packaging",
    "pip",
    "pyparsing",
    "requests"
    "setuptools",
    "six",
]

@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass

@cli.command("generate_bundle")
def generate_bundle():
    """Generate a bundle with Edge packages"""
    _generate_bundle()

def _generate_bundle():
    """Build enthought_edge bundle"""
    shutil.rmtree(ARTIFACT_DIR, ignore_errors=True)
    os.mkdir(ARTIFACT_DIR)
    env = os.environ.copy()
    cmd = [
        "edm",
        "bundle",
        "generate",
        "--platform",
        "rh7-x86_64",
        "--version=3.8",
        "-i",
        "-f",
        BUNDLE_PATH,
    ] + BUNDLE_PACKAGES
    subprocess.run(cmd, env=env, check=True)

@cli.command("build")
@click.option("--tag", default="latest", help="Docker tag to use.")
def build(tag):
    """Build the native example app"""
    click.echo("Building the Native Dash Example App...")

    cwd = os.path.join(SRC_DIR, "frontend")
    subprocess.run(
        ["npm", "install"],
        check=True,
        cwd=cwd,
    )
    cmd = ["npm", "run", "build"]
    subprocess.run(
        cmd,
        check=True,
        cwd=cwd,
    )

    if not os.path.isfile(BUNDLE_PATH):
        _generate_bundle()

    BUNDLE_ARG = os.path.join("ci", "artifacts", BUNDLE_NAME)

    cmd = [
        "docker",
        "build",
        "-t",
        f"{DASH_EXAMPLE_IMAGE}:{tag}",
        "--build-arg",
        f"EDGE_BUNDLE={BUNDLE_ARG}",
        "--build-arg",
        f"CI_IMAGE_REPOSITORY={DASH_EXAMPLE_IMAGE}",
        "--build-arg",
        f"CI_IMAGE_TAG={tag}",
        "-f",
        "Dockerfile",
        MODULE_DIR,
    ]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default="latest", help="Docker tag to use.")
def publish(tag):
    """Publish the native example app"""
    click.echo("Publishing the Native Dash Example App...")
    cmd = ["docker", "push", f"{DASH_EXAMPLE_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default="latest", help="Docker tag to use.")
def start(tag):
    """Start the native example application"""
    click.echo("Starting the JupyterHub container...")
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    env = os.environ.copy()
    env["IMAGE_TAG"] = tag
    subprocess.run(cmd, check=True, env=env)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.group(name="watch")
def watch_cmd():
    pass


@watch_cmd.command(name="backend")
def watch_backend():
    """Start the application and watch backend changes"""

    print(f"\nStart {DASH_EXAMPLE_IMAGE} in files watching mode\n")
    cmd = ["flask", "--app", "app.py", "run"]
    env = os.environ.copy()
    env["FLASK_DEBUG"] = "1"
    env["JUPYTERHUB_API_TOKEN"] = "1"
    env["APP_VERSION"] = "native-dash-app-example running on ci watch backend"
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)


@watch_cmd.command(name="frontend")
def watch_frontend():
    """Start the application and watch frontend changes"""

    cwd = os.path.join(SRC_DIR, "frontend")
    subprocess.run(
        ["npm", "install"],
        check=True,
        cwd=cwd,
    )

    cmd = ["npm", "run", "dev"]
    subprocess.run(
        cmd,
        check=True,
        cwd=cwd,
    )


if __name__ == "__main__":
    cli(prog_name="python -m ci")
