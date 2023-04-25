# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
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


RUN rm /tmp/s6-overlay-noarch.tar.xz
RUN rm /tmp/s6-overlay-x86_64.tar.xz
RUN rm /tmp/nginx-1.24.0-1.el7.ngx.x86_64.rpm

COPY ./container_config/s6-overlay /etc/s6-overlay/

RUN adduser app
RUN chown -R app:app /var/log/nginx
RUN chmod o+rwx /opt

USER app

RUN edm -r /opt/_edm_oauth2_proxy install --version 3.8 click flask requests gunicorn -y
RUN edm -r /opt/_edm_oauth2_proxy run -- python -m pip install "jupyterhub==2.2.2" Flask-Session

COPY --chown=app ./container_config/nginx /opt/nginx/
COPY --chown=app ./oauth2_proxy /opt/oauth2_proxy/

WORKDIR /home/app

# Init command to start s6-overlay
CMD ["/init"]
