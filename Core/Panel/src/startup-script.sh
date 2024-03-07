#!/bin/bash

set -e

# Your app must bind to 127.0.0.1 on port 9000 for the Edge proxy to work.
# However, for local docker execution without a proxy, we need to bind to 0.0.0.0

if [ -z $HOST_ADDRESS ]; then
  # Provide a default if not specified explicitly
  export HOST_ADDRESS='127.0.0.1';
fi

exec edm run -- panel serve app.py --address=${HOST_ADDRESS} --port=9000 --prefix=$JUPYTERHUB_SERVICE_PREFIX --allow-websocket-origin=* --log-level=debug
