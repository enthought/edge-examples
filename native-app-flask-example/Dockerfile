# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edm-centos-7:latest as enthought_edge_stage

ARG EDGE_BUNDLE=ci/artifacts/enthought_edge.zbundle

# install tini
RUN curl -sLO https://github.com/krallin/tini/releases/download/v0.19.0/tini_0.19.0-amd64.rpm && \
    echo "ab82980245169e93f8507f8d9a5fd008f5057df61a06fe46f464c4d624e6424a tini_0.19.0-amd64.rpm" | sha256sum --check && \
    rpm -i tini_0.19.0-amd64.rpm && \
    rm tini_0.19.0-amd64.rpm

RUN adduser app_admin

USER app_admin

WORKDIR /home/app_admin

ADD $EDGE_BUNDLE /home/app_admin/enthought_edge.zbundle

RUN edm env import -f enthought_edge.zbundle edm 

RUN rm enthought_edge.zbundle

# Final image
FROM enthought_edge_stage

USER app_admin

RUN edm install click opencv_python "flask>2" gunicorn requests -y

RUN edm run -- python -m pip install "jupyterhub==2.2.2" dockerspawner "configurable-http-proxy" Flask-Session

COPY --chown=app_admin ./src native-app-flask-example/

WORKDIR /home/app_admin
RUN chmod 777 native-app-flask-example/startup-script.sh

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-native-app-flask-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG

CMD ["tini", "-g", "--", "native-app-flask-example/startup-script.sh"]
