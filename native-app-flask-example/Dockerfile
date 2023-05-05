# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edge-native-base:1.0.0 as edge_flask_stage

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

# Final image
FROM edge_flask_stage 

RUN edm run -- python -m pip install Flask-Session

COPY ./app.location.conf.template /opt/nginx/app.location.conf.template

# Copy startup script and application
COPY --chown=app ./startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/application/ /home/app/application

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-native-app-flask-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG

