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

from .config import discover_ip, EXTERNAL_EXAMPLE_IMAGE, PROJECT_DIR


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass


@cli.command("build")
@click.option("--tag", default="latest", help="Docker tag to use.")
def build(tag):
    """Build external example app"""
    click.echo("Building the External Example App...")
    cmd = ["npm", "install"]
    subprocess.run(cmd, check=True, cwd=os.path.join(PROJECT_DIR, "frontend"))
    cmd = ["npm", "run", "build"]
    subprocess.run(cmd, check=True, cwd=os.path.join(PROJECT_DIR, "frontend"))
    cmd = [
        "docker",
        "build",
        "-t",
        f"{EXTERNAL_EXAMPLE_IMAGE}:{tag}",
        "-f",
        "Dockerfile",
        "..",
    ]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default="latest", help="Docker tag to use.")
def publish(tag):
    """Publish the external example app"""
    click.echo("Publishing the External Example App...")
    cmd = ["docker", "push", f"{EXTERNAL_EXAMPLE_IMAGE}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default="latest", help="Docker tag to use.")
def start(tag):
    """Start the external application"""
    click.echo("Starting the External Example App...")
    start_external_example(tag)
    click.echo("Example app running at: http://localhost:8020")


@cli.command("stop")
def stop():
    """Stop the external application"""
    click.echo("Stopping the External Example App...")
    stop_external_example()
    click.echo("Example app stopped")


def start_external_example(tag):
    """Start the external example app."""
    cmd = ["docker", "run"]
    host = discover_ip()
    env = {
        "SESSION_SECRET_KEY": "external-app-example/test_secrets/secret_key",
        "OAUTH_CLIENT_SECRET": "external-app-example/test_secrets/client_secret",
        "OAUTH_CLIENT_ID": "service-edge-app-default-external-demo",
        "EDGE_BASE_URL": f"http://{host}:8000",
        "OAUTH_REDIRECT_URI": "http://localhost:8020/authorize",
    }
    for key, val in env.items():
        cmd.extend(["--env", f"{key}={val}"])
    cmd.extend(
        [
            "-p",
            "8020:8020",
            "--name",
            "edge-external-demo-app",
            "-d",
            f"{EXTERNAL_EXAMPLE_IMAGE}:{tag}",
        ]
    )
    # subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(cmd, check=True)


def stop_external_example():
    """Stop the external example app."""
    subprocess.run(["docker", "rm", "-f", "edge-external-demo-app"], check=True)


if __name__ == "__main__":
    cli(prog_name="python -m ci")
