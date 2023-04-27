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

from subprocess import Popen
from .config import APP_NAME, IMAGE_NAME, IMAGE_TAG, CONTAINER_NAME
from .builders import DevBuilder, ContainerBuilder
from .contexts import BuildContext, ContainerBuildContext



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
        image_tag=tag
    )

@container.command("run")
@click.pass_obj
def container_run(context):
    """Start the application in container mode"""
    click.echo(
        f"Running {context.app_name} in container {context.container_name}..."
    )
    builder = ContainerBuilder(context)
    builder.run()


@container.command("test")
@click.pass_obj
def container_test(context):
    """Test the application in container mode"""
    click.echo(
        f"Running tests on {context.app_name} using container {context.container_name}..."
    )
    builder = ContainerBuilder(context)
    builder.test()

@container.command("build")
@click.pass_obj
def build(context):
    """Build the application"""
    click.echo(f"Building {context.app_name}...")
    builder = ContainerBuilder(context)
    builder.build()
    click.echo("Done")

@cli.command("publish")
@click.pass_obj
def publish(context):
    """Publish the application image"""
    click.echo(f"Publishing {context.app_name}...")
    builder = ContainerBuilder(context)
    builder.publish()
    click.echo("Done")

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
    click.echo(f"Starting {context.app_name} in dev mode")
    builder = DevBuilder(context)
    builder.run()

@dev.command("test")
@click.pass_obj
def dev_test(context):
    """Run unit tests on the application"""
    click.echo(f"Running tests on {context.app_name}")
    builder = DevBuilder(context)
    builder.test()


if __name__ == "__main__":
    cli(prog_name="python -m ci")
