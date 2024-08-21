#!/bin/bash

set -e

exec edm run -- gunicorn main:app -b 0.0.0.0:9000 -w 1 --access-logfile - --error-logfile - "$@"
