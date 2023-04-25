# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os
import subprocess
import shutil

import click

APP_NAME = "Edge Hello World"
IMAGE_NAME = "quay.io/enthought/edge-hello-world"
IMAGE_VERSION = "1.0.0"
CONTAINER_NAME = "edge-hello-world"
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
SRC_DIR = os.path.join(MODULE_DIR, "src")

CI_DIR = os.path.dirname(__file__)
BUNDLE_NAME = "app_environment.zbundle"
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
BUNDLE_PATH = os.path.join(ARTIFACT_DIR, BUNDLE_NAME)

BUNDLE_PACKAGES = [
    "enthought_edge",
    "appdirs",
    "packaging",
    "pip",
    "pyparsing",
    "setuptools",
    "six",
    "click",
]

@click.group()
@click.option("--edge-api-url", default="https://edge.enthought.com/services/api", help="The API url for Edge")
@click.option("--edge-org-name", default=None, help="Your Edge organization")
@click.option("--edge-api-token", default=None, help="Your Edge API token")
@click.pass_context
def cli(ctx, edge_api_url, edge_org_name, edge_api_token):
    """All commands constituting continuous integration."""
    edge_env = {}
    if edge_api_url is not None:
        edge_env["EDGE_API_SERVICE_URL"] = edge_api_url
    if edge_org_name is not None:
        edge_env["EDGE_API_ORG"] = edge_org_name
    if edge_api_token is not None:
        edge_env["EDGE_API_TOKEN"] = edge_api_token

    ctx.obj = edge_env

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
@click.option("--tag", default=IMAGE_VERSION, help="Docker tag to use.")
def build(tag):
    """Build the application"""
    click.echo(f"Building {APP_NAME}...")

    cmd = [
        "docker",
        "build",
        "-t",
        f"{IMAGE_NAME}:{tag}",
        "-f",
        "Dockerfile",
        MODULE_DIR,
    ]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("publish")
@click.option("--tag", default=IMAGE_VERSION, help="Docker tag to use.")
def publish(tag):
    """Publish the application image"""
    click.echo(f"Publishing {APP_NAME}...")
    cmd = ["docker", "push", f"{IMAGE_NAME}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default=IMAGE_VERSION, help="Docker tag to use.")
@click.pass_obj
def start(obj, tag):
    """Start the application"""
    click.echo("Starting the JupyterHub container...")
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    env = os.environ.copy()
    env["IMAGE_TAG"] = tag
    subprocess.run(cmd, check=True, env=env)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.command("standalone")
@click.option("--tag", default=IMAGE_VERSION, help="Docker tag to use.")
@click.pass_obj
def start(obj, tag):
    """Start the application in standalone mode"""
    env = os.environ.copy()
    remove_container_cmd = [
        "docker",
        "container",
        "rm",
        CONTAINER_NAME
    ]
    subprocess.run(remove_container_cmd, env=env)
    container_envs = [ f"{key}={value}" for key, value in obj.items() ]
    container_envs.append("NO_OAUTH=1")
    cmd = [
        "docker",
        "run",
        "-p",
        "8888:8888",
        "--name",
        CONTAINER_NAME,
    ]
    for container_env in container_envs:
        cmd.append("--env")
        cmd.append(container_env)
    cmd.append(f"{IMAGE_NAME}:{tag}")
    subprocess.run(cmd, check=True, env=env)

@cli.command("watch")
@click.pass_obj
def watch(obj):
    """Start the application and watch backend changes"""

    print(f"\nStart {APP_NAME} in files watching mode\n")
    cmd = ["flask", "--app", "app.py", "run"]
    env = os.environ.copy()
    env["FLASK_DEBUG"] = "1"
    env.update(obj)
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)

if __name__ == "__main__":
    cli(prog_name="python -m ci")
