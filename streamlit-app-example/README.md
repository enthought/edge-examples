# Streamlit App Example

This folder contains a Streamlit application that showcases how to
create a data visualization hosted by Edge native application. 
The streamlit  app is packaged as a Docker image that will be consumed
by the Edge's JupyterHub spawner system.

## Requirements

To build and run the example application you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager
- The `quay.io/enthought/edge-oauth2-app:latest` example image,
  built from the [`edge-oauth2-app`](../edge-oauth2-app/) directory in this repository.

## Set up the development environment

First, you will need to create an EDM environment and install some dependencies.
To do this, use the "bootstrap.py" script:

```commandline
python bootstrap.py
```

This will create the `edge-streamlit-dev` EDM environment.  You may activate it with:

```commandline
edm shell -e edge-streamlit-dev
```

You must also install the NodeJS version of `configurable-http-proxy`:

```commandline
npm install -g configurable-http-proxy
```

## Running the Application

If you are running the application for the first time, you will need to build
the application's Docker image. From within the `streamlit-app-example` directory
run:

```commandline
    python -m ci build
```

Once built, you can run the image from a local JupyterHub session by running:

```commandline
    python -m ci start
```

For your local JupyterHub session, enter any username with the password `password`.

## Local Development

For development purposes, you may run this application outside of a JupyterHub using file
watch modes for automatic reloading. To start the application and watch backend changes:

```commandline
    python -m ci watch
```

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
  
## Requirements for a Edge native application

Edge's JupyterHub spawner will launch a native application's container and provide
environment variables required for routing and authentication. The
`quay.io/enthought/edge-oauth2-app:latest` image built from the 
[`edge-oauth2-app`](../edge-oauth2-app/) directory in this repository implements
the necessary endpoints and workflow for authentication, using these provided
environment variables.

## Registering the Application

Once the application has been tested locally, built using `python -m ci build` and
published using `python -m ci publish`, it can be registered on Edge as an Application tile.
Full instructions for registering the application can be found in [`REGISTER.md`](./REGISTER.md).