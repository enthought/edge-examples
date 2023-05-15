FROM quay.io/enthought/edge-native-base:1.0.0 as edge_panel_app_stage

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle
COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

# Final image
FROM edge_panel_app_stage

COPY ./src/app.location.conf.template /opt/nginx/app.location.conf.template

# Copy startup script and application
COPY --chown=app ./src/startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/application/ /home/app/application