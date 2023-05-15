# Native App Example

This folder contains a Flask + React application that showcases how to
create an Edge native application. The native app is packaged as a docker image that will be consumed by the Edge's JupyterHub spawner system.

## Requirements

To build and run the example application you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 
- The `enthought/edge` EDM repository added to your `~/.edm.yaml` configuration

## Set up the development environment

First, you will need to create an EDM environment and install some dependencies.
To do this, use the "bootstrap.py" script:

```commandline
python bootstrap.py
```

This will create the `edge-native-dev` EDM environment.  You may activate it with:

```commandline
edm shell -e edge-native-dev
```   

## Running the Application

If you are running the application for the first time, you will need to build
the application's Docker image. From within the `native-app-flask-example` directory
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
    python -m ci watch backend
```
To watch the frontend changes:

```commandline
    python -m ci watch frontend
```

## Development and debugging tips

* When making your own app, start with a complete copy of the example app, and
  modify it step by step with your own code.  It's much easier to
  incrementally modify a working system than to develop one from scratch.

* First, try to run the app via `python -m ci watch backend`.  That will run it
  outside of the JupyterHub machinery, and makes it easier to get log output.
  If your app doesn't work for a simple reason like a missing dependency or
  a syntax error, this will catch it.

* When running from a local JupyterHub instance with `python -m ci start`, you
  can use Docker to get the logs from your container.  Use `docker ps` to find
  your app's container, and `docker logs` to view the log output.

## Requirements for an Edge native application

Edge's JupyterHub spawner will launch a native application's container and provide
environment variables for routing and authentication. 

### Using port and URL prefix provided by Edge: 

Once the native application is spawned, the `JUPYTERHUB_SERVICE_URL`
and `JUPYTERHUB_SERVICE_NAME` environment variables will be provided
by Edge. Application authors need to set the listening port and URL prefix of the
application with values extracted from this variable. See the [`ROUTING.md`](./ROUTING.md)
for more details.

### Reporting server activities back to Edge: 

Edge will shut your application down after a while if it is considered inactive.
To avoid this, you will need to report activity back to the server when the user
interacts with your app. 

To report activities, applications can send a POST to the URL provided in the
`JUPYTERHUB_ACTIVITY_URL` environment variable, using the token provided
in `JUPYTERHUB_API_TOKEN`. In this native app example, the 
[`trackactivity` decorator](./src/app.py#L61) is used to perform this POST
whenever any Flask endpoint is accessed.

## Using Edge as an OAuth provider

Edge proxies connections to the single-user server and provides OAuth authentication
for your application. Your application only needs to provide two components to take
advantage of Edge authentication:
- An [OAuth callback handler](./src/app.py#L182) to process Edge OAuth
- An [`authenticated` decorator](./src/app#L90) that protects endpoints requiring authentication

## Registering the Application

Once the application has been tested locally, built using `python -m ci build` and
published using `python -m ci publish`, it can be registered on Edge as an Application tile.
Full instructions for registering the application can be found in [`REGISTER.md`](./REGISTER.md).