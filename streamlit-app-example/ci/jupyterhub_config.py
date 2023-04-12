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


IMAGE_TAG = os.environ.get("IMAGE_TAG", "latest")

c = get_config()  # noqa
temp = tempfile.gettempdir()

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "dummy"
c.DummyAuthenticator.password = "password"

# launch with docker
c.JupyterHub.spawner_class = DockerSpawner

# the hostname/ip that should be used to connect to the hub
c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.redirect_to_server = False

# Don't delete containers when the stop
c.DockerSpawner.remove = False

# docker image for the spawner
c.DockerSpawner.image = f"quay.io/enthought/edge-streamlit-demo:{IMAGE_TAG}"
c.JupyterHub.tornado_settings = {"slow_spawn_timeout": 0}

# File in which to store the database and cookie secret.
c.JupyterHub.cookie_secret_file = path.join(temp, "jupyterhub_cookie_secret")
c.JupyterHub.db_url = path.join(temp, "jupyterhub.sqlite")
c.ConfigurableHTTPProxy.pid_file = path.join(temp, "jupyterhub-proxy.pid")
c.JupyterHub.log_level = 10