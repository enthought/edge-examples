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


RUN adduser app_admin

RUN edm install --version 3.8 click pandas numpy flask requests gunicorn -y

RUN edm run -- python -m pip install "jupyterhub==2.2.2" streamlit streamlit-javascript streamlit-extras Flask-Session

COPY ./container_config /

WORKDIR /home/app_admin
COPY --chown=app_admin ./oauth2_proxy oauth2_proxy/

# Copy startup script and application
COPY --chown=app_admin ./startup-script.sh ./startup-script.sh
RUN chmod +x ./startup-script.sh
COPY --chown=app_admin ./src streamlit-app-example/

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-streamlit-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG

CMD ["/init"]