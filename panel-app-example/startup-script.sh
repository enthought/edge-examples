#!/bin/bash

set -e
exec edm run -- panel serve application/app.py --address="0.0.0.0" --port=9000 --prefix=$JUPYTERHUB_SERVICE_PREFIX --allow-websocket-origin=* --log-level=debug
