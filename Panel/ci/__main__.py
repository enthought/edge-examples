# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    This is the "ci" module for the Panel example.
"""
import click
import os.path as op
import subprocess
import json
import yaml

SRC_ROOT = op.abspath(op.join(op.dirname(__file__), ".."))


def _bundle_image(config: dict) -> str:
    """Assemble a default bundle image name from the configuration settings.
    """
    return "/".join([config["repository"],
                     config["organisation"],
                     config["app_id"]])


@click.group()
@click.pass_context
def cli(ctx):
    """Group for Click commands"""
    config = _load_config_settings()
    ctx.obj = config


@cli.command()
@click.option("--bundle-image", default=None)
@click.option("--rebuild-zbundle", default=False, is_flag=True)
@click.option("--verbose", default=False, is_flag=True)
@click.pass_obj
def build(config, bundle_image, rebuild_zbundle, verbose):
    """Build the Docker image"""

    # Configuration details
    bundle_image = bundle_image or _bundle_image(config)
    version = config["app_version"]
    app_deps = config["app_deps"]

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
        ] + app_deps
        if verbose:
            click.echo(" ".join(cmd))
        subprocess.run(cmd, check=True, cwd=SRC_ROOT)

    # Finally, we run Docker.  The Dockerfile will copy the zbundle into
    # a temp folder and install it.
    cmd = ["docker", "build", "-t", f"{bundle_image}:{version}", "."]
    if verbose:
        click.echo(" ".join(cmd))
    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
@click.option("--bundle-image", default=None)
@click.option("--verbose", default=False, is_flag=True)
@click.pass_obj
def run(config, bundle_image, verbose):
    """Run the Docker image for testing"""

    # Configuration details
    bundle_image = bundle_image or _bundle_image(config)
    container_name = config["app_id"]
    version = config["app_version"]

    # Get values from the dev settings file (API tokens for testing, etc.)
    envs = _load_dev_settings()

    cmd = ["docker", "run", "--rm", "-p", "9000:9000", "--name", container_name]
    for key, value in envs.items():
        cmd += ["--env", f"{key}={value}"]
    cmd += ["--env", "HOST_ADDRESS=0.0.0.0"]
    cmd += [f"{bundle_image}:{version}"]

    if verbose:
        click.echo(" ".join(cmd))
    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
@click.option("--bundle-image", default=None)
@click.option("--verbose", default=False, is_flag=True)
@click.pass_obj
def publish(config, bundle_image, verbose):
    """Publish the Docker image for use with Edge"""

    # Configuration details
    bundle_image = bundle_image or _bundle_image(config)
    version = config["app_version"]

    cmd = ["docker", "push", f"{bundle_image}:{version}"]
    if verbose:
        click.echo(" ".join(cmd))
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


def _load_config_settings():
    """Load the application configuration settings.

    Returns
    -------
    dict
        The configuration settings.
    """
    data = {}
    fpath = op.join(SRC_ROOT, "app_config.yaml")
    if op.exists(fpath):
        with open(fpath, "r") as f:
            data = yaml.safe_load(f)

    if not data:
        raise ValueError("Could not load app_config.yaml")
    return data


if __name__ == "__main__":
    cli()
