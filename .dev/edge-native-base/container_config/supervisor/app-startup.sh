#!/bin/bash

# Main application entrypoint

exec 2>&1
cd /home/app
./startup-script.sh
