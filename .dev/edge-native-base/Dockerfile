# Multi-stage build

# Intermediate image with enthought_edge package included via bundle
FROM quay.io/enthought/edm-centos-7:latest

# Install nginx
RUN yum -y install openssl pcre2 gettext 
ADD http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.24.0-1.el7.ngx.x86_64.rpm /tmp
RUN rpm -iv /tmp/nginx-1.24.0-1.el7.ngx.x86_64.rpm

RUN rm /tmp/nginx-1.24.0-1.el7.ngx.x86_64.rpm

RUN adduser app
RUN chown -R app:app /var/log/nginx
RUN mkdir /var/log/supervisord
RUN chown -R app:app /var/log/supervisord
RUN chmod o+rwx /opt

USER app

RUN edm -r /opt/_edm_oauth2_proxy install --version 3.8 click flask requests gunicorn -y
RUN edm -r /opt/_edm_oauth2_proxy run -- python -m pip install "jupyterhub==2.2.2" Flask-Session supervisor

COPY --chown=app ./container_config/supervisor /opt/supervisor/
COPY --chown=app ./container_config/nginx /opt/nginx/
COPY --chown=app ./oauth2_proxy /opt/oauth2_proxy/
COPY --chown=app ./default /home/app/default/
COPY --chown=app ./startup-script.sh /home/app

WORKDIR /home/app

CMD ["edm", "-r", "/opt/_edm_oauth2_proxy", "run", "--", "supervisord", "-n", "-c", "/opt/supervisor/supervisord.conf"]
