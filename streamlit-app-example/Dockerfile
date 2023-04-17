FROM quay.io/enthought/edm-centos-7:latest

# install tini
RUN curl -sLO https://github.com/krallin/tini/releases/download/v0.19.0/tini_0.19.0-amd64.rpm && \
    echo "ab82980245169e93f8507f8d9a5fd008f5057df61a06fe46f464c4d624e6424a tini_0.19.0-amd64.rpm" | sha256sum --check && \
    rpm -i tini_0.19.0-amd64.rpm && \
    rm tini_0.19.0-amd64.rpm

RUN adduser app_admin
USER app_admin
WORKDIR /home/app_admin

RUN edm envs create edm --version 3.8 && edm cache purge --yes
RUN edm run -- python -m pip install --no-cache-dir \
    click pandas numpy requests "jupyterhub==2.2.2" \
    streamlit streamlit-javascript streamlit-extras

COPY --chown=app_admin ./src streamlit-app-example/
RUN chmod 777 streamlit-app-example/startup-script.sh

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-streamlit-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG


CMD ["tini", "-g", "--", "streamlit-app-example/startup-script.sh"]
