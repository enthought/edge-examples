#!/bin/bash
exec 2>&1
set -e
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8
cd /opt
echo "Starting OAuth2 Proxy"
edm -r /opt/_edm_oauth2_proxy run -- python -m oauth2_proxy.wsgi