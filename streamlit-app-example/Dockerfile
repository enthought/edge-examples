FROM quay.io/enthought/edge-oauth2-app:latest 

# Add packages to the application environment
RUN edm run -- python -m pip install --no-cache-dir \
    click pandas numpy requests "jupyterhub==2.2.2" \
    streamlit streamlit-javascript streamlit-extras

# Copy startup script and application
COPY ./startup-script.sh /opt/startup-script.sh
RUN chmod +x /opt/startup-script.sh
COPY ./src /opt/application
