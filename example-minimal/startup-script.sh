#!/bin/bash

set -e

exec edm run -- gunicorn main:app -b 127.0.0.1:9000
