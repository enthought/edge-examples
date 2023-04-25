#!/bin/bash
set -e
exec edm run -- python -m application.wsgi
