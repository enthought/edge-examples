# Edge OAuth2 Native Base Image 

This folder contains the source for building the `quay.io/enthought/edge-native-base` Docker
image. This image is used as a base image for example native apps to implement
authentication functionality.


## Requirements

To build and run the example application you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

## Set up the development environment

First, you will need to create an EDM environment and install some dependencies.
To do this, use the "bootstrap.py" script:

```commandline
python bootstrap.py
```

This will create the `edge-native-base` EDM environment.  You may activate it with:

```commandline
edm shell -e edge-native-base
```

You must also install the NodeJS version of `configurable-http-proxy`:

```commandline
npm install -g configurable-http-proxy
```

## Copying CI Tools

When creating a new example based on `edge-native-base`, you must:

- Copy [the `ci` directory](./ci) to the root of the new example
- Copy [`./bootstrap.py`](./bootstrap.py) to the root of the new example
- Copy [`./config.py'](./config.py) to the root of the new example and configure it

Application files should reside in [`src/application`] in the new example.

## Configuring CI

[`./config.py`](./config.py) contains CI settings, including the image name
and tag for CI commands. *It is critical to set the `IMAGE_TAG` value before
building or pushing a new image to prevent overwriting a published image that
might break compatibility for downstream consumers of `edge-native-base`.* It should
*never* be set to `latest`.

## Development of this Image

`edge-native-base` can be built with the `python -m ci2 build` command and pushed
with the `python -m ci2 publish` command. When a new local version is built, it
should be tested by altering one of the downstream examples to use it as a base.
The downstream example should still be runnable with its CI in `container`
and `preflight` modes.

## Architecture

This image includes the following components that are copied via its Dockerfile:

- [`./container_config/nginx`](./container_config/nginx/) contains configuration templates
  for `nginx`. Only `app.location.conf.template` should be overwritten in a downstream
  example Dockerfile if the application cannot be served at `http://localhost:9000/`
- [`./container_config/s6-overlay`](./container_config/s6-overlay/) contains configuration
  files and scripts for the s6-overlay service, which manages the `oauth2_proxy` subprocess,
  the `nginx` subprocess and client application subprocess.
- [`oauth2_proxy`](./oauth2_proxy/) is the Flask service that manages authentication state
  on behalf of the client application