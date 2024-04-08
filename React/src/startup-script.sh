#!/bin/bash

set -e

# Your app must bind to 127.0.0.1 on port 9000 for the Edge proxy to work.
# However, for local docker execution without a proxy, we need to bind to 0.0.0.0

if [ -z $HOST_ADDRESS ]; then
  # Provide a default if not specified explicitly
  export HOST_ADDRESS='127.0.0.1';
fi

exec edm run -- gunicorn application.app:app -b ${HOST_ADDRESS}:9000 --workers 1
