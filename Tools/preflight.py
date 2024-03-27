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

import logging
import os
import os.path as op
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from unittest import TestCase
from urllib.parse import urlparse
import shutil

import click
import requests
from click import secho

RETRIES = 5
BACKOFF = 5

transient_errors = [502, 503, 504]

@click.command()
@click.argument("image")
@click.option(
    "--app-log", default="edge-app-log.txt", help="Write app log here on failure"
)
@click.option(
    "--hub-log", default="edge-hub-log.txt", help="Write JupyterHub log here on failure"
)
def preflight(image, app_log, hub_log):
    """Test an application's Docker image for compatibility with Edge."""

    if "/" not in image or ":" not in image:
        secho(f"Invalid image name '{image}'.", fg="red")
        secho("Image name should be of the form 'example.com/org/repo:tag'")
        sys.exit(1)

    app_log = op.abspath(app_log)
    hub_log = op.abspath(hub_log)

    with run_jupyterhub(image, app_log, hub_log), requests.Session() as s:
        with check("Get the login page"):
            r = s.get("http://localhost:8000/hub/login")
            r.raise_for_status()

        with check("Perform login"):
            response = s.post(
                "http://localhost:8000/hub/login",
                data={"username": "edgeuser", "password": "password"},
                allow_redirects=True,
            )
            response.raise_for_status()

        with check("Tell the spawner to start"):
            response = s.get("http://localhost:8000/hub/spawn/edgeuser")
            response.raise_for_status()

        with check("Wait for the application to start"):
            # Collect all redirects
            redirects = []
            for attempt in range(RETRIES):
                try:
                    response = s.get("http://localhost:8000/user/edgeuser")
                    if response.status_code in transient_errors:
                        print(f"Attempt {attempt + 1}: Received {response.status_code} error, retrying after {BACKOFF} seconds...")
                    else:
                        response.raise_for_status()
                        redirects = redirects + [urlparse(r.url).path for r in response.history]
                        if "spawn-pending" not in response.url:
                            break
                except Exception as e:
                    print(f"Attempt {attempt + 1}: Error encountered: {e}. Retrying after {BACKOFF} seconds...")
                time.sleep(BACKOFF)
            else:
                raise AssertionError("Application failed to start")

        with check("Fetch application home page"):
            response = s.get("http://localhost:8000/user/edgeuser")
            response.raise_for_status()
            redirects = redirects + [urlparse(r.url).path for r in response.history]
            if not response.url.startswith("http://localhost:8000/user/edgeuser"):
                raise AssertionError("Application home page did not load")
            if not (response.status_code >= 200 and response.status_code < 300):
                raise AssertionError("Application home page not served with 2XX")

        with check("Check authorization flow"):
            if "/user/edgeuser/oauth_start/" not in redirects:
                raise AssertionError("OAuth2 'start' is missing")
            if "/hub/api/oauth2/authorize" not in redirects:
                raise AssertionError("OAuth2 'authorize' is missing")
            if "/user/edgeuser/oauth_callback/" not in redirects:
                raise AssertionError("OAuth2 'callback' is missing")

        with check("Check unknown users cannot access app"):
            response = requests.get(
                "http://localhost:8000/user/edgeuser/", allow_redirects=True
            )
            if response.url.startswith("http://localhost:8000/user/edgeuser"):
                raise AssertionError("Response URL points to app")


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
def run_jupyterhub(image, app_log, hub_log):
    """Run JupyterHub, cleaning up after ourselves.

    Log files will be be created if there is an exception while running
    JupyterHub.

    Parameters
    ----------
    image : Str
        Name of Docker image to run as single-user server (app)
    app_log : Str
        Path to write the application log file.
    hub_log : Str
        Path to write the JupyterHub log file.

    Returns
    -------
    Context manager
    """
    with tempfile.TemporaryDirectory() as tempdir:
        temp_app_log = op.join(tempdir, "app.log")
        temp_hub_log = op.join(tempdir, "hub.log")

        container_name = "preflight-container"
        with open(op.join(tempdir, "jupyterhub_config.py"), "w") as f:
            f.write(JH_CONFIG)

        cmd = ["jupyterhub", "-f", "jupyterhub_config.py"]
        env = os.environ.copy()
        env.update({"IMAGE": image, "CONTAINER_NAME": container_name})

        try:
            with open(temp_hub_log, "w") as f:
                process = subprocess.Popen(
                    cmd, env=env, cwd=tempdir, stdout=f, stderr=subprocess.STDOUT
                )

                try:
                    with check("Starting JupyterHub"):
                        time.sleep(BACKOFF)
                        if process.poll() is not None:
                            raise AssertionError("JupyterHub failed to start")
                    yield
                finally:
                    time.sleep(2)
                    try:
                        process.terminate()
                    except Exception:
                        pass
                    time.sleep(2)
                    try:
                        process.kill()
                    except Exception:
                        pass

        except:
            # Copy logs out only if there was an error during the run
            with open(temp_app_log, "w") as f:
                f.write(fetch_logs_and_destroy(container_name))
            shutil.copy(temp_app_log, app_log)
            shutil.copy(temp_hub_log, hub_log)
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


JH_CONFIG = """\
import os
import socket
import tempfile
from os import path

from dockerspawner import DockerSpawner

image = os.environ.get("IMAGE")
container_name = os.environ.get("CONTAINER_NAME")

container_env = {}
for name in ("EDGE_API_TOKEN", "EDGE_API_SERVICE_URL", "EDGE_API_ORG"):
    val = os.environ.get(name)
    if val is not None:
        container_env[name] = val

def discover_hub_ip():
    "Find the right IP address for JupyterHub."
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(("10.255.255.255", 1))
        ip = st.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        st.close()
    return ip

c = get_config()  # noqa
temp = tempfile.gettempdir()

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "dummy"
c.DummyAuthenticator.password = "password"

# launch with docker
c.JupyterHub.spawner_class = DockerSpawner

# the hostname/ip that should be used to connect to the hub
c.JupyterHub.hub_ip = discover_hub_ip()
c.JupyterHub.ip = "127.0.0.1"
c.JupyterHub.bind_url = "http://127.0.0.1:8000"
c.JupyterHub.redirect_to_server = False

# Containers will be auto-removed when they stop.
c.DockerSpawner.remove = False
c.DockerSpawner.environment = container_env

# docker image for the spawner
c.DockerSpawner.image = image
c.DockerSpawner.name_template = container_name

c.JupyterHub.tornado_settings = {"slow_spawn_timeout": 0}

# File in which to store the database and cookie secret.
c.JupyterHub.cookie_secret_file = path.join(temp, "jupyterhub_cookie_secret")
c.ConfigurableHTTPProxy.pid_file = path.join(temp, "jupyterhub-proxy.pid")
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.autoRewrite = True
c.JupyterHub.log_level = "DEBUG"
"""


if __name__ == "__main__":
    preflight()
