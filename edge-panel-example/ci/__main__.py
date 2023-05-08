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

from .config import BUNDLE_PACKAGES
from .config import CONTAINER_BUILDER_CLS as ContainerBuilder
from .config import DEV_BUILDER_CLS as DevBuilder
from .config import IMAGE_TAG, LINT_ENV_NAME
from .config import PREFLIGHT_BUILDER_CLS as PreflightBuilder
from .contexts import ContainerBuildContext, DevBuildContext, PreflightBuildContext

CI_DIR = os.path.dirname(__file__)
BUNDLE_NAME = "app_environment.zbundle"
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
BUNDLE_PATH = os.path.join(ARTIFACT_DIR, BUNDLE_NAME)


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass


@cli.command("generate_bundle")
@click.option(
    "--edm-config",
    default=None,
    help="EDM configuration path"
)
@click.option(
    "--edm-token",
    default=None,
    help="EDM token"
)
def generate_bundle(edm_config, edm_token):
    """Generate a bundle with Edge packages"""
    _generate_bundle(edm_config=edm_config, edm_token=edm_token)


def _generate_bundle(edm_config=None, edm_token=None):
    """Build enthought_edge bundle"""
    shutil.rmtree(ARTIFACT_DIR, ignore_errors=True)
    os.mkdir(ARTIFACT_DIR)
    env = os.environ.copy()
    base_cmd = ["edm"]
    if edm_config is not None:
        print(f"Using edm configuration {edm_config}")
        base_cmd.append("-c")
        base_cmd.append(edm_config)
    if edm_token is not None:
        print("Using edm token ***")
        base_cmd.append("-t")
        base_cmd.append(edm_token)
    cmd = base_cmd + [
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


@cli.command()
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Whether or not to apply isort and black formatting.",
)
@click.option(
    "--rebuild", is_flag=True, default=False, help="Force-rebuild style checking env"
)
def style(apply, rebuild):
    """Run formatting checks"""

    cmd = ["edm", "envs", "list"]
    proc = subprocess.run(cmd, check=True, capture_output=True)

    # Build env if needed
    if rebuild or (LINT_ENV_NAME not in proc.stdout.decode("utf8")):
        cmd = ["edm", "envs", "create", LINT_ENV_NAME, "--force", "--version", "3.8"]
        subprocess.run(cmd, check=True)

        cmd = [
            "edm",
            "install",
            "-e",
            LINT_ENV_NAME,
            "-y",
            "black",
            "click",
            "flake8",
            "isort",
            "pyyaml",
        ]
        subprocess.run(cmd, check=True)

    # Then run checking commands
    commands = [
        (["isort", "."], ["--check", "--diff"], "isort check failed"),
        (["black", "."], ["--check"], "Black check failed"),
        (["python", "-m", "flake8"], [], "Flake8 check failed"),
    ]

    for cmd, options, fail_message in commands:
        if not apply:
            cmd = cmd + options
        cproc = subprocess.run(["edm", "run", "-e", LINT_ENV_NAME, "--"] + cmd)
        rc = cproc.returncode
        if rc is not None and rc != 0:
            # Ensure user can see why the check failed
            click.echo(cproc.stderr)
            raise click.ClickException(fail_message)


@cli.group("preflight")
@click.option(
    "--edge-settings-file",
    default=None,
    help="A json file with E2E test settings",
)
@click.option("--tag", default=IMAGE_TAG, help="Docker tag to use.")
@click.pass_context
def preflight(ctx, edge_settings_file, tag):
    """CLI group for container commands"""
    ctx.obj = PreflightBuildContext(
        edge_settings_file=edge_settings_file, image_tag=tag
    )


@preflight.command("run")
@click.pass_obj
def preflight_run(context):
    """Start the application"""
    click.echo("Starting JupyterHub...")
    builder = PreflightBuilder(context)
    builder.run()


@preflight.command("test")
@click.option("--verbose", is_flag=True, default=False, help="Verbose test output")
@click.pass_obj
def preflight_test(context, verbose):
    """Start the application"""
    click.echo("Running preflight checks...")
    builder = PreflightBuilder(context)
    builder.test(verbose)


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
        edge_settings_file=edge_settings_file, image_tag=tag
    )


@container.command("run")
@click.pass_obj
def container_run(context):
    """Start the application in container mode"""
    click.echo(f"Running {context.app_name} in container {context.container_name}...")
    builder = ContainerBuilder(context)
    builder.run()


@container.command("test")
@click.option("--verbose", is_flag=True, default=False, help="Verbose test output")
@click.pass_obj
def container_test(context, verbose):
    """Test the application in container mode"""
    click.echo(
        f"Running tests on {context.app_name} "
        + f"using container {context.container_name}..."
    )
    builder = ContainerBuilder(context)
    builder.test(verbose)


@container.command("build")
@click.pass_obj
def build(context):
    """Build the application"""
    click.echo(f"Building {context.image} image for {context.app_name}...")
    builder = ContainerBuilder(context)
    builder.build()
    click.echo("Done")


@container.command("publish")
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
    ctx.obj = DevBuildContext(edge_settings_file=edge_settings_file)


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
