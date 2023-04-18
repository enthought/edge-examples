#!/bin/bash

set -e

exec edm run -- streamlit run streamlit-app-example/app.py --server.headless true --server.port 9000