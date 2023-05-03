#!/bin/bash
set -e
if [ -z $JUPYTERHUB_SERVICE_PREFIX]; then
    export JUPYTERHUB_SERVICE_PREFIX='/';
fi
envsubst '${JUPYTERHUB_SERVICE_PREFIX}' < /opt/nginx/nginx.conf.template > /opt/nginx/nginx.conf;
envsubst '${JUPYTERHUB_SERVICE_PREFIX}' < /opt/nginx/app.location.conf.template > /opt/nginx/app.location.conf;
echo "Starting nginx"
nginx -c /opt/nginx/nginx.conf;