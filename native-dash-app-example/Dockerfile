# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edm-centos-7:latest as enthought_edge_stage

ARG EDGE_BUNDLE=ci/artifacts/app_environment.zbundle

# install tini
RUN curl -sLO https://github.com/krallin/tini/releases/download/v0.19.0/tini_0.19.0-amd64.rpm && \
    echo "ab82980245169e93f8507f8d9a5fd008f5057df61a06fe46f464c4d624e6424a tini_0.19.0-amd64.rpm" | sha256sum --check && \
    rpm -i tini_0.19.0-amd64.rpm && \
    rm tini_0.19.0-amd64.rpm

RUN adduser app_admin

USER app_admin

WORKDIR /home/app_admin

COPY $EDGE_BUNDLE /home/app_admin/app_environment.zbundle

RUN edm env import -f app_environment.zbundle edm 

RUN rm app_environment.zbundle

# Final image
FROM enthought_edge_stage

USER app_admin

RUN edm run -- python -m pip install "jupyterhub==2.2.2" dockerspawner "configurable-http-proxy" Flask-Session pandas

COPY --chown=app_admin ./src native-dash-app-example/

WORKDIR /home/app_admin
RUN chmod 777 native-dash-app-example/startup-script.sh

# We don't have time for a new quay repo for this test, so re-use native with
# a custon TAG
#ARG CI_IMAGE_REPOSITORY=quay.io/enthought/native-dash-app-demo
#ARG CI_IMAGE_TAG=latest
ARG CI_IMAGE_REPOSITORY=quay.io/enthought/native-dash-app-demo
ARG CI_IMAGE_TAG=dash
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG

CMD ["tini", "-g", "--", "native-dash-app-example/startup-script.sh"]
