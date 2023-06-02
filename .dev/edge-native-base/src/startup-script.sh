#!/bin/bash

set -e
cd /home/app/default

exec edm -r /opt/_edm_oauth2_proxy run -- gunicorn app:app -b 127.0.0.1:9000
