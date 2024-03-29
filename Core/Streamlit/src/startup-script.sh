#!/bin/bash

set -e

# Your app must bind to 127.0.0.1 on port 9000 for the Edge proxy to work.
# However, for local docker execution without a proxy, we need to bind to 0.0.0.0

if [ -z $HOST_ADDRESS ]; then
  # Provide a default if not specified explicitly
  export HOST_ADDRESS='127.0.0.1';
fi

if [[ -z "${JUPYTERHUB_SERVICE_PREFIX}" ]]; then
  export STREAMLIT_SERVER_BASE_URL_PATH="/"
else
  export STREAMLIT_SERVER_BASE_URL_PATH="${JUPYTERHUB_SERVICE_PREFIX}"
fi

exec edm run -- streamlit run app.py --server.headless true --server.address=${HOST_ADDRESS} --server.port 9000
