#!/bin/bash

set -e
exec edm run -e application -- streamlit run application/app.py --server.headless true --server.port 9000