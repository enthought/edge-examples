#!/bin/bash
set -e
cd /home/app/default
exec edm -r /opt/_edm_oauth2_proxy run -- python -m http.server 9000