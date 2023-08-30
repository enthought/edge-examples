
FROM quay.io/enthought/edm-centos-7:3.4.0

# Install nginx
RUN yum -y install epel-release && yum -y clean all  && rm -rf /var/cache
RUN yum -y install openssl pcre2 gettext supervisor wget sudo && yum -y clean all  && rm -rf /var/cache

RUN wget http://nginx.org/packages/centos/7/x86_64/RPMS/nginx-1.24.0-1.el7.ngx.x86_64.rpm \
	&& rpm -iv nginx-1.24.0-1.el7.ngx.x86_64.rpm \
	&& rm nginx-1.24.0-1.el7.ngx.x86_64.rpm

RUN adduser app
RUN usermod -aG wheel app
RUN echo "app ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN chown -R app:app /var/log/nginx
RUN mkdir /var/log/supervisord
RUN chown -R app:app /var/log/supervisord
RUN chmod o+rwx /opt

USER app

RUN edm -r /opt/_edm_oauth2_proxy install --version 3.8 flask gunicorn requests -y \
	&& edm -r /opt/_edm_oauth2_proxy run -- python -m pip install --no-cache-dir "jupyterhub==2.2.2" Flask-Session \
	&& edm -r /opt/_edm_oauth2_proxy cache purge --yes

COPY --chown=app ./src/container_config/supervisor /opt/supervisor/
RUN chmod +x /opt/supervisor/scripts/*.sh
COPY --chown=app ./src/container_config/nginx /opt/nginx/
COPY --chown=app ./src/oauth2_proxy /opt/oauth2_proxy/
COPY --chown=app ./src/default /home/app/default/
COPY --chown=app ./src/startup-script.sh /home/app

RUN chmod +x /home/app/startup-script.sh

WORKDIR /home/app

CMD ["/usr/bin/supervisord", "-n", "-c", "/opt/supervisor/supervisord.conf"]
