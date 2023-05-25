import click
import os.path as op
import subprocess
import sys
import os
import json

SRC_ROOT = op.abspath(op.join(op.dirname(__file__), ".."))

# Docker image will be tagged "IMAGE:VERSION"
VERSION = "0.0.1"
IMAGE = "quay.io/enthought/edge-example-minimal"

# These will go into the built Docker image.  You may wish to modify this
# minimal example to pin the dependencies, or use a bundle file to define them.
APP_DEPENDENCIES = ["flask", "gunicorn", "enthought_edge"]


@click.group()
def cli():
    """Group for Click commands"""
    pass


@cli.command()
@click.option("--rebuild-zbundle", default=False, is_flag=True)
def build(rebuild_zbundle):
    """Build the Docker image"""

    # Build bundle with dependencies
    fname = "app_environment.zbundle"
    if not op.exists(op.join(SRC_ROOT, fname)) or rebuild_zbundle:
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
        ] + APP_DEPENDENCIES
        subprocess.run(cmd, check=True, cwd=SRC_ROOT)

    cmd = ["docker", "build", "-t", f"{IMAGE}:{VERSION}", "."]
    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
def run():
    """Run the Docker image for testing"""

    # Get values from the .env file (API tokens for testing, etc.)
    # For testing, also disable the OAuth2 machinery.
    envs = _load_dev_settings()
    envs["EDGE_DISABLE_AUTH"] = "1"

    cmd = ["docker", "run", "-p", "8888:8888"]
    for key, value in envs.items():
        cmd += ["--env", f"{key}={value}"]
    cmd += [f"{IMAGE}:{VERSION}"]
    subprocess.run(cmd, check=True, cwd=SRC_ROOT)


@cli.command()
def run_in_jupyter():
    """Run the Docker image in a local JupyterHub environment"""
    cmd = ["jupyterhub", "-f", "ci/jupyterhub_config.py"]

    env = os.environ.copy()
    env.update(
        {
            "IMAGE": f"{IMAGE}:{VERSION}",
            "CONTAINER_NAME": IMAGE.split("/")[-1],
        }
    )
    env.update(_load_dev_settings())

    subprocess.run(cmd, env=env)


@cli.command()
def publish():
    """Publish the Docker image for use with Edge"""
    pass


def _load_dev_settings():
    """Load dev_settings.json file"""
    fpath = op.join(SRC_ROOT, "dev_settings.json")
    if not op.exists(fpath):
        return {}
    with open(fpath, "r") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if k.startswith("EDGE_")}


if __name__ == "__main__":
    cli()
