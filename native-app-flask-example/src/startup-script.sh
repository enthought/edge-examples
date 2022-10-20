#!/bin/bash

set -e

exec edm run -- python -m native-app-flask-example.wsgi
