# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os
import subprocess

import click

EDGE_OAUTH2_APP_IMAGE = "quay.io/enthought/edge-oauth2-app"
EDGE_OAUTH2_APP_CONTAINER = "edge-oauth2-app"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
SRC_DIR = os.path.join(MODULE_DIR, "src")


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass

@cli.command("build")
@click.option("--tag", default="latest", help="Docker tag to use.")
def build(tag):
    """Build the OAuth2 example app"""
    click.echo("Building the OAuth2 Example App...")

    cmd = [
        "docker",
        "build",
        "-t",
        f"{EDGE_OAUTH2_APP_IMAGE}:{tag}",
        "-f",
        "Dockerfile",
        MODULE_DIR,
    ]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default="latest", help="Docker tag to use.")
def publish(tag):
    """Publish the OAuth2 example app"""
    click.echo("Publishing the OAuth2 Example App...")
    cmd = ["docker", "push", f"{EDGE_OAUTH2_APP_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default="latest", help="Docker tag to use.")
def start(tag):
    """Start the OAuth2 example application"""
    click.echo("Starting the JupyterHub container...")
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    env = os.environ.copy()
    env["IMAGE_TAG"] = tag
    subprocess.run(cmd, check=True, env=env)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.command("standalone")
@click.option("--tag", default="latest", help="Docker tag to use.")
def start(tag):
    """Start the OAuth2 example application in standalone mode"""
    env = os.environ.copy()
    remove_container_cmd = [
        "docker",
        "container",
        "rm",
        EDGE_OAUTH2_APP_CONTAINER
    ]
    subprocess.run(remove_container_cmd, env=env)
    cmd = [
        "docker",
        "run",
        "-p",
        "8888:8888",
        "--name",
        EDGE_OAUTH2_APP_CONTAINER,
        "-e",
        "NO_OAUTH=1",
        f"{EDGE_OAUTH2_APP_IMAGE}:{tag}"
    ]
    subprocess.run(cmd, check=True, env=env)

@cli.command("watch")
def watch():
    """Start the application and watch backend changes"""

    print(f"\nStart example application in files watching mode\n")
    cmd = ["flask", "--app", "app.py", "run"]
    env = os.environ.copy()
    env["FLASK_DEBUG"] = "1"
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)

if __name__ == "__main__":
    cli(prog_name="python -m ci")
