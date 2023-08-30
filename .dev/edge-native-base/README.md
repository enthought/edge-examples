# Edge Native Base Image 

This folder contains the source for building the
`quay.io/enthought/edge-native-base` Docker image. This image is used as a
base image for apps, enabling them to integrate with Edge more easily.  It
handles OAuth2 integration with JupyterHub, along with automatic activity
reporting (keep-alive) to enable idle-app shutdown to work properly.

## Requirements

To build and run the example application you will need:

- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

Run ``npm install -g configurable-http-proxy`` to install a proxy module
needed by JupyterHub. 

Run ``bootstrap.py`` and use the ``python -m ci`` commands for development.

