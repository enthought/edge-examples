#!/bin/bash

# Main application entrypoint

exec 2>&1
cd /home/app
echo "Starting app"
./startup-script.sh
