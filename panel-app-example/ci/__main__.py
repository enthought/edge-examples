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

PANEL_EXAMPLE_IMAGE = "quay.io/enthought/edge-panel-demo"
PANEL_EXAMPLE_CONTAINER = "edge-panel-demo"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
SRC_DIR = os.path.join(MODULE_DIR, "src")


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass


@cli.command("build")
@click.option("--tag", default="latest", help="Docker tag to use.")
def build(tag):
    """Build the panel example app"""
    click.echo("Building the panel Example App...")

    cmd = [
        "docker",
        "build",
        "-t",
        f"{PANEL_EXAMPLE_IMAGE}:{tag}",
        "--build-arg",
        f"CI_IMAGE_REPOSITORY={PANEL_EXAMPLE_IMAGE}",
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
    """Publish the panel example app"""
    click.echo("Publishing the panel Example App...")
    cmd = ["docker", "push", f"{PANEL_EXAMPLE_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default="latest", help="Docker tag to use.")
def publish(tag):
    """Publish to quay.io/enthought/edge-panel-demo"""
    click.echo("Publishing the panel Example App...")
    cmd = ["docker", "push", f"{PANEL_EXAMPLE_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default="latest", help="Docker tag to use.")
def start(tag):
    """Start the panel example application"""
    click.echo("Starting the JupyterHub container...")
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    env = os.environ.copy()
    env["IMAGE_TAG"] = tag
    subprocess.run(cmd, check=True, env=env)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.command("watch")
def watch_cmd():
    """Start the application and watch changes"""

    print(f"\nStart {PANEL_EXAMPLE_CONTAINER} in files watching mode\n")
    cmd = ["panel", "serve", "app.py"]
    env = os.environ.copy()
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)


if __name__ == "__main__":
    cli(prog_name="python -m ci")
