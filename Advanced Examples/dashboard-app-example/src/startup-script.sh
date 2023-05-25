#!/bin/bash

set -e

exec edm run -- python -m dashboard-app-example.wsgi
