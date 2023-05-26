# Edge OAuth2 Native Base Image 

This folder contains the source for building the
`quay.io/enthought/edge-native-base` Docker image. This image is used as a
base image for example native apps to implement authentication
functionality.

## Requirements

To build and run the example application you will need:

- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

Run ``bootstrap.py`` and use the ``python -m ci`` commands for development.
They match the ones used in the examples.
