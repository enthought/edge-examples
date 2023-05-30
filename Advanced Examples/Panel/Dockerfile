# This is the Dockerfile for the Enthought Edge "Streamlit" example.
# 
# We use "edge-native-base" as the base image.  This is a Centos-7 based image
# which includes EDM, as well as a small proxy server which automatically 
# handles OAuth2 communication between your app and Edge.
#
# EDM dependencies for the app are brought in via a .zbundle file.  This avoids
# the need to pass your EDM token and/or a custom edm.yaml into the Dockerfile.
#
# We perform a two-stage build, to avoid including the .zbundle in the layers
# of the published image.


# IMPORTANT: Please do not define any of the EDGE_* environment variables, or
# any of the JUPYTERHUB_* variables, directly in this file. They will be set
# automatically when running in Edge, or by the "ci" module when running
# locally.


# First stage

ARG BASE_IMAGE=quay.io/enthought/edge-native-base:1.0.1

FROM $BASE_IMAGE as stage_one

ARG EDGE_BUNDLE=app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes


# Second stage

FROM $BASE_IMAGE

COPY --from=stage_one --chown=app /home/app/.edm /home/app/.edm

# Make any global changes (yum install, e.g.) in the second stage.
# Don't change the user, and in particular don't make the user "root".
RUN sudo echo "(Run yum via sudo if needed)"

# Copy startup script and application.
# Note: the startup script must be placed in /home/app for the base image
# machinery to pick it up.

COPY --chown=app ./src/startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/app.py /home/app/app.py

COPY ./src/app.location.conf.template /opt/nginx/app.location.conf.template


