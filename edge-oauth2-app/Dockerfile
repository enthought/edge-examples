FROM quay.io/enthought/edm-centos-7:latest

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

RUN edm environments create oauth2_proxy --version 3.8
RUN edm install -e oauth2_proxy click flask requests gunicorn -y
RUN edm run -e oauth2_proxy  -- python -m pip install "jupyterhub==2.2.2" Flask-Session

COPY ./container_config /
COPY ./oauth2_proxy /opt/oauth2_proxy/

# Create default EDM environment
RUN edm envs create edm --version 3.8 && edm cache purge --yes
RUN edm envs create application --version 3.8 && edm cache purge --yes

# Init command to start s6-overlay
CMD ["/init"]

# User application goes here

RUN edm install -e application click "flask>2" gunicorn requests -y

# Copy startup script and application
COPY ./startup-script.sh /opt/startup-script.sh
RUN chmod +x /opt/startup-script.sh
COPY ./src /opt/application