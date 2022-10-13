#!/bin/bash

set -e

exec edm run -- gunicorn -w 2 -b 0.0.0.0:8020 --timeout 60 --log-file - external-app-example.wsgi
