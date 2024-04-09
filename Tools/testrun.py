# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Script for checking an app's Docker image for Edge compatibility.
"""

import os
import os.path as op
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager

import click
import requests
from click import secho

RETRIES = 5
BACKOFF = 5


@click.command()
@click.argument("image")
@click.option(
    "--app-log", default="edge-app-log.txt",
    help="Write app log here on failure"
)
def testrun(image, app_log):
    """Test an application's Docker image for compatibility with Edge."""

    if "/" not in image or ":" not in image:
        secho(f"Invalid image name '{image}'.", fg="red")
        secho("Image name should be of the form 'example.com/org/repo:tag'")
        sys.exit(1)

    app_log = op.abspath(app_log)

    with run_application(image, app_log), requests.Session() as s:
        with check("Access the application root"):
            response = s.get("http://localhost:9000")
            response.raise_for_status()
            if not (200 <= response.status_code < 400):
                raise AssertionError(
                    "Application home page error")


@contextmanager
def check(info):
    """Print success or failure, and raise SystemExit in the latter case.

    Parameters
    ----------
    info : Str
        Message to print at the start of the line.

    Returns
    -------
    Context manager
    """
    secho(f"{info}... ", nl=False)
    try:
        yield
    except Exception as e:
        secho(f"FAILED: {e}", fg="red")
        sys.exit(1)
    else:
        secho("PASSED", fg="green")


@contextmanager
def run_application(image, app_log):
    """Run application in Docker, cleaning up after ourselves.

    Log files will be created if there is an exception.

    Parameters
    ----------
    image : Str
        Name of Docker image to run as single-user server (app)
    app_log : Str
        Path to write the application log file.

    Returns
    -------
    Context manager
    """
    with tempfile.TemporaryDirectory() as tempdir:
        temp_app_log = op.join(tempdir, "app.log")

        container_name = "testrun-container"

        cmd = ["docker", "run", "--rm", "-p", "9000:9000", "--name",
               container_name,
               "--env", "HOST_ADDRESS=0.0.0.0",
               image]
        env = os.environ.copy()

        try:
            process = subprocess.Popen(cmd, env=env, cwd=tempdir)

            try:
                with check("Starting Application"):
                    time.sleep(BACKOFF)
                    if process.poll() is not None:
                        raise AssertionError("Application failed to start")
                yield
            finally:
                with check("Stopping Application"):
                    cmd = ["docker", "stop", container_name]
                    subprocess.run(cmd, check=True)

        except:
            # Copy logs out only if there was an error during the run
            with open(temp_app_log, "w") as f:
                f.write(fetch_logs_and_destroy(container_name))
            shutil.copy(temp_app_log, app_log)
            raise


def fetch_logs_and_destroy(container_name):
    """Fetch logs from the container, and unconditionally remove it.

    Parameters
    ----------
    container_name : Str
        Name of the Docker container for which to dump logs.

    Returns
    -------
    Str
        Log output (or empty string).
    """
    cmd = ["docker", "logs", container_name]
    proc = subprocess.run(cmd, capture_output=True)
    logs = ""
    if proc.stdout is not None:
        logs = proc.stdout.decode("utf8", errors="ignore")

    cmd = ["docker", "rm", container_name]
    subprocess.run(cmd, capture_output=True)
    return logs


if __name__ == "__main__":
    testrun()
