# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edge-native-base:1.0.0 as edge_hello_world_stage

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

# Final image
FROM edge_hello_world_stage 

# Install dependencies for Flask Hello World in the default EDM environment
RUN edm install click "flask>2" gunicorn requests -y

# Copy startup script and application
COPY --chown=app ./startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src /home/app/application
