# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edge-native-base:1.0.0 as edge_native_flask_stage

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

# Final image
FROM edge_native_flask_stage

# Install dependencies for Flask Hello World in the default EDM environment
RUN edm run -- pip install Flask-Session

# Copy location template
COPY ./app.location.conf.template /opt/nginx/app.location.conf.template

# Copy startup script and application
COPY --chown=app ./startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/application/ /home/app/application

ARG CI_IMAGE=quay.io/enthought/edge-native-app-flask-demo:latest
ENV APP_VERSION=$CI_IMAGE