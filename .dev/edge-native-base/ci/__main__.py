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

from config import CONTAINER_BUILDER_CLS, DEV_BUILDER_CLS, PREFLIGHT_BUILDER_CLS
from config import IMAGE_TAG

from .contexts import ContainerBuildContext, DevBuildContext, PreflightBuildContext

CI_DIR = os.path.dirname(__file__)
BUNDLE_NAME = "app_environment.zbundle"
ARTIFACT_DIR = os.path.join(CI_DIR, "artifacts")
BUNDLE_PATH = os.path.join(ARTIFACT_DIR, BUNDLE_NAME)


@click.group()
def cli():
    """All commands constituting continuous integration."""
    pass


@cli.group("preflight")
@click.option(
    "--edge-settings-file",
    default="edge_settings.json",
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
    builder = PREFLIGHT_BUILDER_CLS(context)
    builder.run()


@preflight.command("test")
@click.option("--verbose", is_flag=True, default=False, help="Verbose test output")
@click.pass_obj
def preflight_test(context, verbose):
    """Start the application"""
    click.echo("Running preflight checks...")
    builder = PREFLIGHT_BUILDER_CLS(context)
    builder.test(verbose)


@cli.group("container")
@click.option(
    "--edge-settings-file",
    default="edge_settings.json",
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
    builder = CONTAINER_BUILDER_CLS(context)
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
    builder = CONTAINER_BUILDER_CLS(context)
    builder.test(verbose)


@container.command("build")
@click.option(
    "--generate-bundle", is_flag=True, default=False, help="Regenerate bundle"
)
@click.option("--edm-config", default=None, help="EDM configuration path")
@click.option("--edm-token", default=None, help="EDM token")
@click.pass_obj
def container_build(context, generate_bundle, edm_config, edm_token):
    """Build the application"""
    click.echo(f"Building {context.image} image for {context.app_name}...")
    builder = CONTAINER_BUILDER_CLS(context)
    builder.build(
        generate_bundle=generate_bundle, edm_config=edm_config, edm_token=edm_token
    )
    click.echo("Done")


@container.command("generate_bundle")
@click.option("--edm-config", default=None, help="EDM configuration path")
@click.option("--edm-token", default=None, help="EDM token")
@click.pass_obj
def container_generate_bundle(context, edm_config, edm_token):
    """Generate a bundle with Edge packages"""
    builder = CONTAINER_BUILDER_CLS(context)
    builder.generate_bundle(edm_config=edm_config, edm_token=edm_token)
    click.echo("Done")


@container.command("publish")
@click.pass_obj
def container_publish(context):
    """Publish the application image"""
    click.echo(f"Publishing {context.app_name}...")
    builder = CONTAINER_BUILDER_CLS(context)
    builder.publish()
    click.echo("Done")


@cli.group("dev")
@click.option(
    "--edge-settings-file",
    default="edge_settings.json",
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
    builder = DEV_BUILDER_CLS(context)
    builder.run()


@dev.command("test")
@click.pass_obj
def dev_test(context):
    """Run unit tests on the application"""
    click.echo(f"Running tests on {context.app_name}")
    builder = DEV_BUILDER_CLS(context)
    builder.test()


if __name__ == "__main__":
    cli(prog_name="python -m ci")
