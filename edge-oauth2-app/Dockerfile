# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edm-centos-7:latest as edge_oauth2_app_stage

# Install nginx
RUN yum -y install openssl pcre2 gettext
ADD http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.24.0-1.el7.ngx.x86_64.rpm /tmp
RUN rpm -iv /tmp/nginx-1.24.0-1.el7.ngx.x86_64.rpm

# Install s6-overlay
ARG S6_OVERLAY_VERSION=3.1.4.1
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

RUN edm -r /opt/_edm_oauth2_proxy install --version 3.8 click flask requests gunicorn -y
RUN edm -r /opt/_edm_oauth2_proxy run -- python -m pip install "jupyterhub==2.2.2" Flask-Session

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle

COPY $EDGE_BUNDLE /tmp/app_environment.zbundle

# Create a default EDM environment using the enthought_edge bundle
RUN edm env import -f /tmp/app_environment.zbundle edm && edm cache purge --yes

RUN rm /tmp/app_environment.zbundle
RUN rm /tmp/s6-overlay-noarch.tar.xz
RUN rm /tmp/s6-overlay-x86_64.tar.xz
RUN rm /tmp/nginx-1.24.0-1.el7.ngx.x86_64.rpm

# Final image
FROM edge_oauth2_app_stage

# Install dependencies for Flask Hello World in the default EDM environment
RUN edm install click "flask>2" gunicorn requests -y

COPY ./container_config /
COPY ./oauth2_proxy /opt/oauth2_proxy/

# Copy startup script and application
COPY ./startup-script.sh /opt/startup-script.sh
RUN chmod +x /opt/startup-script.sh
COPY ./src /opt/application

# Init command to start s6-overlay
CMD ["/init"]
