#!/bin/bash

set -e
exec edm run -e application -- python -m application.wsgi
