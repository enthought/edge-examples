#!/bin/bash

set -e
set
exec edm run -- panel serve panel-app-example/app.py --address="0.0.0.0" --port=8888 --prefix=$JUPYTERHUB_SERVICE_PREFIX --allow-websocket-origin=* --log-level=debug
