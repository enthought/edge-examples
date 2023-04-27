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

from .config import APP_NAME, IMAGE_NAME, IMAGE_TAG, CONTAINER_NAME
from .context import BuildContext, ContainerBuildContext

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
@click.option("--tag", default=IMAGE_TAG, help="Docker tag to use.")
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
@click.option("--tag", default=IMAGE_TAG, help="Docker tag to use.")
def publish(tag):
    """Publish the application image"""
    click.echo(f"Publishing {APP_NAME}...")
    cmd = ["docker", "push", f"{IMAGE_NAME}:{tag}"]
    subprocess.run(cmd, check=True)
    click.echo("Done")


@cli.command("start")
@click.option("--tag", default=IMAGE_TAG, help="Docker tag to use.")
@click.option(
    "--edge-settings-file",
    default=None,
    help="A json file with E2E test settings",
)
def start(tag, edge_settings_file):
    """Start the application"""
    click.echo("Starting the JupyterHub container...")
    edge_settings = _get_edge_settings(edge_settings_file)
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]
    env = os.environ.copy()
    env["IMAGE_NAME"] = IMAGE_NAME
    env["IMAGE_TAG"] = tag
    env.update(edge_settings)
    subprocess.run(cmd, check=True, env=env)
    click.echo("JupyterHub is running at: http://127.0.0.1:8888")


@cli.group("container")
@click.option(
    "--edge-settings-file",
    default=None,
    help="A json file with E2E test settings",
)
@click.option("--tag", default=IMAGE_TAG, help="Docker tag to use.")
@click.pass_context
def container(ctx, edge_settings_file, tag):
    """CLI group for container commands"""
    ctx.obj = ContainerBuildContext(
        edge_settings_file=edge_settings_file,
        mode="container",
        image_tag=tag
    )

@container.command("run")
@click.pass_obj
def container_run(context):
    """Start the application in container mode"""
    env = os.environ.copy()
    remove_container_cmd = [
        "docker",
        "container",
        "rm",
        context.container_name
    ]
    subprocess.run(remove_container_cmd, env=env)
    container_envs = [f"{key}={value}" for key, value in context.env.items()]
    cmd = [
        "docker",
        "run",
        "-p",
        "8888:8888",
        "--name",
        context.container_name
    ]
    for container_env in container_envs:
        cmd.append("--env")
        cmd.append(container_env)
    cmd.append(f"{context.image_name}:{context.image_tag}")
    subprocess.run(cmd, check=True, env=env)

@cli.group("dev")
@click.option(
    "--edge-settings-file",
    default=None,
    help="A json file with E2E test settings",
)
@click.pass_context
def dev(ctx, edge_settings_file):
    """CLI group for dev commands"""
    ctx.obj = BuildContext(edge_settings_file=edge_settings_file, mode="dev")

@dev.command("run")
@click.pass_obj
def dev_run(context):
    """Start the application and watch backend changes"""
    print(f"\nStart {APP_NAME} in files watching mode\n")
    cmd = ["flask", "--app", "app.py", "run"]
    env = os.environ.copy()
    env.update(context.env)
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)

@dev.command("test")
@click.pass_obj
def dev_test(context):
    """Run unit tests on the application"""
    cmd = ["pytest"]
    env = os.environ.copy()
    env.update(context.env)
    subprocess.run(cmd, check=True, env=env, cwd=SRC_DIR)


if __name__ == "__main__":
    cli(prog_name="python -m ci")
