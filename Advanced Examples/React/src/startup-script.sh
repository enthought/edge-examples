#!/bin/bash

set -e

# This file will be automatically picked up by the edge-native-base machinery,
# which runs a small proxy server in front of your app.  Your app must bind to
# 127.0.0.1 on port 9000 for this to work.  The container itself will
# serve on port 8888, through the proxy.

exec edm run -- gunicorn application.app:app -b 127.0.0.1:9000 --workers 1
