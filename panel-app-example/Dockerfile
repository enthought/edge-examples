FROM quay.io/enthought/edge-native-base:1.0.0

# Install panel dependencies
RUN edm install click panel pandas numpy matplotlib -y

COPY ./app.location.conf.template /opt/nginx/app.location.conf.template

# Copy startup script and application
COPY --chown=app ./startup-script.sh /home/app/startup-script.sh
RUN chmod +x /home/app/startup-script.sh
COPY --chown=app ./src/application/ /home/app/application