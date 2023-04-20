FROM quay.io/enthought/edge-oauth2-app:latest 

# Install panel dependencies
RUN edm install click panel pandas numpy matplotlib -y

COPY ./nginx.conf.template /etc/nginx/nginx.conf.template

# Copy startup script and application
COPY ./startup-script.sh /opt/startup-script.sh
RUN chmod +x /opt/startup-script.sh
COPY ./src /opt/application
