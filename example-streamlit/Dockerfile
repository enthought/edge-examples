# This is the Dockerfile for the Enthought Edge "streamlit" example.
# 
# We use "edge-native-base" as the base image.  This is a Centos-7 based image
# which includes EDM, as well as a small proxy server which automatically 
# handles OAuth2 communication between your app and Edge.
#
# EDM dependencies for the app are brought in via a .zbundle file.  We perform
# a two-stage build, to avoid including the .zbundle in the layers of the 
# published image.

ARG BASE_IMAGE=quay.io/enthought/edge-native-base:1.0.1

FROM $BASE_IMAGE as stage_one

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

# Add packages to the application environment
RUN edm run -- python -m pip install --no-cache-dir \
    streamlit streamlit-javascript streamlit-extras

# Second stage
FROM $BASE_IMAGE

COPY --from=stage_one --chown=app /home/app/.edm /home/app/.edm

# Copy startup script and application
COPY --chown=app ./src/startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/application/ /home/app/application
