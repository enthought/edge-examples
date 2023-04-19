# Edge OAuth2 Native Base Image 

This folder contains the source for building the `quay.io/enthought/edge-oauth2-app` Docker
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

This will create the `edge-oauth2-dev` EDM environment.  You may activate it with:

```commandline
edm shell -e edge-oauth2-dev
```

You must also install the NodeJS version of `configurable-http-proxy`:

```commandline
npm install -g configurable-http-proxy
```

## Running the Application

If you are running the application for the first time, you will need to build
the application's Docker image. From within the `dashboard-app-example` directory
run:

```commandline
    python -m ci build
```

Once built, you can run the image from a local JupyterHub session by running:

```commandline
    python -m ci start
```

For your local JupyterHub session, enter any username with the password `password`.

## Using the `quay.io/enthought/edge-oauth2-app` Base Image

This base image is designed to run:

* An `oauth2_proxy` component
* A simple Hello World Flask application, with source files in `/opt/application` and
  a [`startup-script.sh`](./startup-script.sh) file. The Flask application is internally 
  served within the container at `http://localhost:9000`
* An nginx proxy that serves the application and the `oauth2_proxy`
* The `s6-overlay` process manager, with configuration files in the
  [`container_config`](./container_config/) directory

When extending using this image as a base for an Edge native application,
be sure to:

* Have your Dockerfile install your EDM requirements to the `application` environment
* Have your Dockerfile copy the application to `/opt/application`
* Replace [`startup-script.sh`](./startup-script.sh) contents with a script that
  launches your application within the `application` edm environment
* The application should bind to the localhost port 9000 with a base URL of `/`. `nginx`
  will proxy requests to `http://localhost:9000` within the application container

**Important**: Do not replace the `CMD` directive in your Dockerfile.

## Development and debugging tips

* When making your own app, start with a complete copy of the example app, and
  modify it step by step with your own code.  It's much easier to
  incrementally modify a working system than to develop one from scratch.

* First, try to run the app via `python -m ci watch`.  That will run it
  outside of the JupyterHub machinery, and makes it easier to get log output.
  If your app doesn't work for a simple reason like a missing dependency or
  a syntax error, this will catch it.

* When running from a local JupyterHub instance with `python -m ci start`, you
  can use Docker to get the logs from your container.  Use `docker ps` to find
  your app's container, and `docker logs` to view the log output.
