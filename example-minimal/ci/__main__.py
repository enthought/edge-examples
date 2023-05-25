import click
import os.path as op
import subprocess
import sys
import os

# Docker image will be tagged "IMAGE:VERSION"
VERSION = "0.0.1"
IMAGE = "quay.io/enthought/edge-example-minimal"

# These will go into the built Docker image
APP_DEPENDENCIES = ["flask", "gunicorn", "enthought_edge"]


ROOT = op.abspath(op.join(op.dirname(__file__), ".."))


@click.group()
def cli():
    """Group for Click commands"""
    pass


@cli.command()
@click.option("--rebuild-bundle", default=False, is_flag=True)
def build(rebuild_bundle):
    """Build the Docker image"""

    # Build bundle with dependencies
    fname = "app_environment.zbundle"
    if not op.exists(op.join(ROOT, fname)) or rebuild_bundle:
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
        subprocess.run(cmd, check=True, cwd=ROOT)

    # Create the Docker image
    cmd = ["docker", "build", "-t", f"{IMAGE}:{VERSION}", "."]
    subprocess.run(cmd, check=True, cwd=ROOT)


@cli.command()
def run():
    """Run the Docker image for testing"""

    # Get values from the .env file (API tokens for testing, etc.)
    # For testing, also disable the OAuth2 machinery.
    envs = _load_env()
    envs["EDGE_DISABLE_AUTH"] = "1"

    cmd = ["docker", "run", "-p", "8888:8888"]
    for key, value in envs.items():
        cmd += ["--env", f"{key}={value}"]
    cmd += [f"{IMAGE}:{VERSION}"]
    subprocess.run(cmd, check=True, cwd=ROOT)


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
    env.update(_load_env())

    subprocess.run(cmd, env=env)


@cli.command()
def publish():
    """Publish the Docker image for use with Edge"""
    pass


def _load_env():
    """Load .env file"""
    data = {}
    path = op.join(ROOT, ".env")
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            parts = line.split("=")
            if len(parts) != 2:
                msg = f"Bad line (must be KEY=VALUE): {line}"
                raise ValueError(msg)
            data[parts[0]] = parts[1]
    return data


if __name__ == "__main__":
    cli()
