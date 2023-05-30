#!/bin/bash

set -e

# This file will be automatically picked up by the edge-native-base machinery,
# which runs a small proxy server in front of your app.  Your app must bind to
# 127.0.0.1 on port 9000 for this to work.  The container itself will
# serve on port 8888, through the proxy.

# Please note the --prefix option is required, in conjunction with the
# app.location.conf.template file, in order to make Panel compatible with
# JupyterHub's routing.

exec edm run -- panel serve app.py --address="127.0.0.1" --port=9000 --prefix=$JUPYTERHUB_SERVICE_PREFIX --allow-websocket-origin=* --log-level=debug
