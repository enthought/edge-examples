#!/bin/bash

set -e

exec edm run -- python -m native-dash-app-example.wsgi
