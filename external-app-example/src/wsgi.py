# Enthought product code
#
# (C) Copyright 2010-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This file and its contents are confidential information and NOT open source.
# Distribution is prohibited.

""" Helper module for Gunicorn. """

from .app import create_app

class ReverseProxied(object):
    """Helper WSGI class to pass the correct scheme (https vs http)
    to Flask, so that url_for generates OAuth callback URLs
     with the correct scheme when served through a proxy"""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

application = create_app()
application.wsgi_app = ReverseProxied(application.wsgi_app)