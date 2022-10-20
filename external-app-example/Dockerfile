FROM quay.io/enthought/edm-centos-7:latest

# install tini
RUN curl -sLO https://github.com/krallin/tini/releases/download/v0.19.0/tini_0.19.0-amd64.rpm && \
    echo "ab82980245169e93f8507f8d9a5fd008f5057df61a06fe46f464c4d624e6424a tini_0.19.0-amd64.rpm" | sha256sum --check && \
    rpm -i tini_0.19.0-amd64.rpm && \
    rm tini_0.19.0-amd64.rpm

RUN adduser app_admin
USER app_admin

RUN edm install authlib flask gunicorn requests -y
RUN edm run -- python -m pip install Flask-Session

WORKDIR /home/app_admin
COPY --chown=app_admin external-app-example external-app-example/

RUN chmod 777 external-app-example/startup-script.sh

CMD ["tini", "-g", "--", "external-app-example/startup-script.sh"]
