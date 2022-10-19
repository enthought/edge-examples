# Native App Example

This folder contains a Flask + React application that showcases how to
create an Edge native application. The native app is packaged as a docker image that will be consumed by the Edge's JupyterHub spawner system.

## Requirements

To build and run the example application you will need:
- [Docker](https://docke.com)
- [Node JS}(https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

## Set up the development environment

First, you will need to create an EDM environment named `dev_env` and install some dependencies.

```commandline
edm install -e dev_env --version 3.8 -y click requests opencv_python "flask>2" && \
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
the application's Docker image. From within the `native-app-flask-example` directory
run:

```commandline
    python -m ci build
```

Once built, you can run the image from a local JupyterHub session by running:

```commandline
    python -m ci start
```

For your local JupyterHub session, your username is `dummy` and the password is `password`.

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
will be available. Users need to set the listening port and URL prefix of the
application with values extracted from this variable. In this native app example,
the binding information is provided to the [`wsgi` application](./src/wsgi.py#L43).

### Reporting server activities back to Edge: 

Edge will shut your application down after a while if it is considered inactive.
To avoid this, you will need to report activity back to the server when the user
interacts with your app. 

To report activities, users can send a POST to the URL provided in the
`JUPYTERHUB_ACTIVITY_URL` environment variable, using the token provided
in `JUPYTERHUB_API_TOKEN`. In this native app example, the 
[`trackactivity` decorator](./src/app.py#L61) is used to perform this POST
whenever any Flask endpoint is accessed.

## Using Edge as an OAuth provider

Edge proxies connections to the single-user server, therefore
it's the job of the native app (`Flask` in this case) to provide user authentication.
To simplify the process, Edge can act as an OAuth provider for the
single-user server. The authentication flow generally goes like this:

* Create a [JupyterHub `HubOAuth` authenticator](./src/app.py#L54)
with the `JUPYTERHUB_API_TOKEN` environment variable. This object provides methods
to generate user tokens and identify Edge users accessing the native app via the
generated tokens.

* When a non-authenticated user makes a request to access your application, the server
[redirects the user](./src/app.py#L106) to the Edge login page with extra information:
    - the [`state`](./src/app.py#L107) of the request, including the redirect
      target to your application
    - the [cookie name](./src/app.py#L109) for storing OAuth state.

* After the user is authenticated with Edge, the browser is redirected to your application's
[OAuth callback handler](./src/app.py#L182). Your application needs to [generate an Edge
token](./src/app.py#L196) from the OAuth flow's code and store it in a user session.

* Finally authenticated user is [redirected](./src/app.py#L199) back to the original URL.

Any further requests to your native application can be using the `HubOAuth` and
the token stored in the user's session. In this native app example, this is done using
an [`authenticated` route decorator](./src/app#L90).
