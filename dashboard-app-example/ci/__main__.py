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

NATIVE_EXAMPLE_IMAGE = "quay.io/enthought/edge-dashboard-demo"
NATIVE_EXAMPLE_CONTAINER = "edge-dashboard-demo"
MODULE_DIR = os.path.dirname(__file__)


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass


@cli.command("build")
@click.option("--tag", default="latest", help="Docker tag to use.")
def build(tag):
    """Build the native example app"""
    click.echo("Building the Native Example App...")

    cwd = os.path.join(MODULE_DIR, "..", "frontend")
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

    cmd = [
        "docker",
        "build",
        "-t",
        f"{NATIVE_EXAMPLE_IMAGE}:{tag}",
        "-f",
        "Dockerfile",
        "..",
    ]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default="latest", help="Docker tag to use.")
def publish(tag):
    """Publish the native example app"""
    click.echo("Publishing the Native Example App...")
    cmd = ["docker", "push", f"{NATIVE_EXAMPLE_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
def start():
    """Start the native example application"""
    click.echo("Starting the JupyterHub container...")
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    subprocess.run(cmd, check=True)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.group(name="watch")
def watch_cmd():
    pass


@watch_cmd.command(name="backend")
def watch_backend():
    """Start the application and watch backend changes"""

    print(f"\nStart {NATIVE_EXAMPLE_CONTAINER} in files watching mode\n")
    cmd = ["flask", "--app", "app.py", "--debug", "run"]
    env = os.environ.copy()
    env["DEV_MODE"] = "1"
    subprocess.run(cmd, check=True, env=env)


@watch_cmd.command(name="frontend")
def watch_frontend():
    """Start the application and watch frontend changes"""

    cwd = os.path.join(MODULE_DIR, "..", "frontend")
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
