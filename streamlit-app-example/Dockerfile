FROM quay.io/enthought/edge-oauth2-native:latest 

# Create default EDM environment
RUN edm envs create edm --version 3.8 && edm cache purge --yes
RUN edm run -- python -m pip install --no-cache-dir \
    click pandas numpy requests "jupyterhub==2.2.2" \
    streamlit streamlit-javascript streamlit-extras

WORKDIR /home/app_admin

# Copy startup script and application
COPY --chown=app_admin ./startup-script.sh ./startup-script.sh
RUN chmod +x ./startup-script.sh
COPY --chown=app_admin ./src streamlit-app-example/

ARG CI_IMAGE_REPOSITORY=quay.io/enthought/edge-streamlit-demo
ARG CI_IMAGE_TAG=latest
ENV APP_VERSION=$CI_IMAGE_REPOSITORY:$CI_IMAGE_TAG
