# Native App Example

This folder contains a Flask + React application that showcases how to
create a dashboard hosted by Edge native application. The dashboard app is packaged as 
a Docker image that will be consumed by the Edge's JupyterHub spawner system.

## Requirements

To build and run the example application you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

## Set up the development environment

First, you will need to create an EDM environment named `dev_env` and install some dependencies.

```commandline
edm install -e dev_env --version 3.8 -y click requests "flask>2" && \
edm run -e dev_env -- python -m pip install "jupyterhub==2.2.2" \
    dockerspawner \
    "configurable-http-proxy" \
    Flask-Session
```   

Once you have created the `dev_env` environment, you may activate it with:

```commandline
edm shell -e dev_env
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


## Requirements for a Edge native application

Edge's JupyterHub spawner will launch a native application's container and provide
environment variables for routing and authentication.

### Using port and URL prefix provided by `JupyterHub`: 

Once the native application is spawned, the environment variable `JUPYTERHUB_SERVICE_URL`
will be available. Application authors need to set the listening port and URL prefix of the
application with values extracted from this variable. In this native app example,
the binding information is provided to the [`wsgi` application](./src/wsgi.py#L43).

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