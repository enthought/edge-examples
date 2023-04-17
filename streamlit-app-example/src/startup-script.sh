#!/bin/bash

set -e
set
exec edm run -- streamlit run streamlit-app-example/app.py --server.headless true --server.port 8888 --server.baseUrlPath $JUPYTERHUB_SERVICE_PREFIX
