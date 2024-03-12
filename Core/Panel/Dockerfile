# This is the Dockerfile for the Enthought Edge "Panel" core example.
# 
# We use "edm-centos-7" as the base image.  This is a Centos-7 based image
# which includes EDM.
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

ARG BASE_IMAGE=quay.io/enthought/edm-centos-7:latest

FROM $BASE_IMAGE as stage_one

ARG EDGE_BUNDLE=app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

RUN adduser app
USER app
WORKDIR /home/app

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes


# Second stage

FROM $BASE_IMAGE as stage_two

RUN adduser app
USER app
WORKDIR /home/app

COPY --from=stage_one --chown=app /home/app/.edm /home/app/.edm

# Make any global changes (yum install, e.g.) in the second stage.
# Don't change the user, and in particular don't make the user "root".

# Copy startup script and application.
# Note: the startup script must be placed in /home/app for the base image
# machinery to pick it up.

COPY --chown=app ./src/startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/app.py /home/app/app.py

CMD ["/home/app/startup-script.sh"]
