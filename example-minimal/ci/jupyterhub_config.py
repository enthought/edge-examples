# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

"""
    Config file for local JupyterHub.  This is used by the "ci" module for
    running your app in test mode.
"""
import os
import socket
import tempfile
from os import path

from dockerspawner import DockerSpawner


# These are set by the CI script, based on the parameters at the top
# of ci/__main__.py.
image = os.environ.get("IMAGE")
container_name = os.environ.get("CONTAINER_NAME")


# These, if they exist, are forwarded by the CI script from settings in
# the 'dev_settings.json' file.
container_env = {}
for name in ("EDGE_API_TOKEN", "EDGE_API_SERVICE_URL", "EDGE_API_ORG"):
    val = os.environ.get(name):
    if val is not None:
        container_env[name] = val


def discover_hub_ip():
    """Find the right IP address for JupyterHub."""
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
c.DockerSpawner.remove = True
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
