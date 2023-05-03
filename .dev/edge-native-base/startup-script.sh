#!/bin/bash
set -e
cd /home/app/default
exec edm run -- python -m http.server 9000