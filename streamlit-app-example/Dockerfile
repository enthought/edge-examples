FROM quay.io/enthought/edm-centos-7:latest

# install tini
RUN curl -sLO https://github.com/krallin/tini/releases/download/v0.19.0/tini_0.19.0-amd64.rpm && \
    echo "ab82980245169e93f8507f8d9a5fd008f5057df61a06fe46f464c4d624e6424a tini_0.19.0-amd64.rpm" | sha256sum --check && \
    rpm -i tini_0.19.0-amd64.rpm && \
    rm tini_0.19.0-amd64.rpm

RUN adduser app_admin
USER app_admin

RUN edm install --version 3.8 click pandas numpy requests -y

RUN edm run -- python -m pip install "jupyterhub==2.2.2" streamlit streamlit-javascript

WORKDIR /home/app_admin
COPY --chown=app_admin ./src streamlit-app-example/

WORKDIR /home/app_admin
RUN chmod 777 streamlit-app-example/startup-script.sh

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-streamlit-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG

CMD ["tini", "-g", "--", "streamlit-app-example/startup-script.sh"]
