# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

import os
import socket
import tempfile
from os import path

from dockerspawner import DockerSpawner


def discover_ip():
    """Find the IP address we are connected to."""
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(("10.255.255.255", 1))
        ip = st.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        st.close()
    return ip


IMAGE = os.environ.get("IMAGE")
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
EDGE_API_TOKEN = os.environ.get("EDGE_API_TOKEN")
EDGE_API_SERVICE_URL = os.environ.get("EDGE_API_SERVICE_URL")
EDGE_API_ORG = os.environ.get("EDGE_API_ORG")
if (
    EDGE_API_TOKEN is not None
    and EDGE_API_SERVICE_URL is not None
    and EDGE_API_ORG is not None
):
    container_env = {
        "EDGE_API_TOKEN": EDGE_API_TOKEN,
        "EDGE_API_ORG": EDGE_API_ORG,
        "EDGE_API_SERVICE_URL": EDGE_API_SERVICE_URL,
    }
else:
    container_env = {}

c = get_config()  # noqa
temp = tempfile.gettempdir()

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "dummy"
c.DummyAuthenticator.password = "password"

# launch with docker
c.JupyterHub.spawner_class = DockerSpawner

# the hostname/ip that should be used to connect to the hub
c.JupyterHub.hub_ip = discover_ip()
c.JupyterHub.ip = "127.0.0.1"
c.JupyterHub.bind_url = "http://127.0.0.1:8000"
c.JupyterHub.redirect_to_server = False

# Don't delete containers when the stop
c.DockerSpawner.remove = True
c.DockerSpawner.environment = container_env

# docker image for the spawner
c.DockerSpawner.image = IMAGE
c.DockerSpawner.name_template = CONTAINER_NAME

c.JupyterHub.tornado_settings = {"slow_spawn_timeout": 0}

# File in which to store the database and cookie secret.
c.JupyterHub.cookie_secret_file = path.join(temp, "jupyterhub_cookie_secret")
c.ConfigurableHTTPProxy.pid_file = path.join(temp, "jupyterhub-proxy.pid")
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.autoRewrite = True
c.JupyterHub.log_level = "DEBUG"
