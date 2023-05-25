# Externally-Hosted App Example

This folder contains a Flask + React application that showcases how to
integrate an external web app with Edge, by using JupyterHub as the OAuth2 provider.

## Pre-Requisites

To integrate your external web app with Edge, you need to know the hostname of where
your app will be hosted. For this demonstration, we will integrate the application deployed
to [`https://edge-external-app-demo.platform-devops.enthought.com`](https://edge-external-app-demo.platform-devops.enthought.com)


## Creating an Application Tile in Edge

The first step in integrating your external web app with Edge is creating a tile
on Edge's Home. As an Edge organization developer, you can use the code below
to perform this task from within an Edge notebook. Be sure to substitute the
`external_hostname` with your application's hostname.


```python
from edge.apps.application import Application
from edge.apps.app_version import AppKindEnum, AppVersion

external_hostname = "https://edge-external-app-demo.platform-devops.enthought.com"

ICON = (
  "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABmJLR0QA/w"
  "D/AP+gvaeTAAABfklEQVRoge2ZTU7DMBBGHz9bECpLWAI36ZIdEvQa5Rpw"
  "CFQhtaq66o5wErgCWSR7KAvbUrGaFI8Tu5XmSZbjuFK/mS/jNjYoiqLsMp"
  "fAHKiBVeJWAwvgOkZ8mUG430rgQhLAfAfEuzZrEnnQEkANnAQG3RcVcLZp"
  "oi2AlTe+7UzO/1h6441aDxMI6ZUcASz5m11/HMTeO3Cc8Lv8LDeNg2pNHQ"
  "jAZdbPtCjzDnUgAK2BTWgN5CalAw4/01H/sfbeAQ0gN5IaOAJGwNBeF8AE"
  "+LHzna4y25AEMALu18Z3GPGTThQFIglgaPsx8NmhFhGSGhjYPrt4iPsdeM"
  "G8NxfAFPj25sVvWSHErEID4Bx4sM3xEaUokBgHxpgEPGHq4tXef/Q+16sT"
  "EgdK269vc/hbMMmQOFBgHpln714WJAFMbe+W0zdatv76RnfmctPmQAWcph"
  "KyhcbN3TYH3vvRIkK0SNwAX+Q/GyiBK0kAYE5GZhgLUwuvMIcsYvGKoij9"
  "8ws479akcYBsnQAAAABJRU5ErkJggg=="
)

app = Application('edge-external-app-demo', True)

version1 = AppVersion(
    app_id=app.app_id,
    version="1.0.0",
    title="Edge External App Demo, v1.0.0",
    description="Demonstration of an external application",
    icon=ICON,
    kind=AppKindEnum.External,
    link=external_hostname,
)

edge.applications.add_application(app)
edge.applications.add_app_version(version1)
```

After running this code, return to the Home screen in Edge. You should see a tile labeled
*Edge External App Demo v1.0.0*.

## Registering The Application

As an Edge organization developer you must register a new Edge OAuth Client by
providing a `redirect_uri` for the application that you added in the previous step.
You can use the code below to perform this task from within an Edge notebook.

```python
result = edge.applications.register_oauth_client(app.app_id, f"{external_hostname}/authorize")
result
```

The result will look similar to this:

```python
{'client_id': 'service-edge-app-default-edge-external-app-demo',
 'client_secret': 'RANDOM_CLIENT_SECRET',
 'redirect_uri': 'https://edge-external-app-demo.platform-devops.enthought.com/authorize'}
 ```

These values (along with Edge's base URL `https://edge-dev-main.platform-devops.enthought.com`)
should be provided to your application when you deploy it.

## Configuring Your Application

Edge handles OAuth for your external web application. In this example,
we provide  `client_id`, `client_secret` and `redirect_uri` to the
[`authlib`](./src/app.py#L31) library.

The requirements for authentication in this example Flask application are handled
in [`api/auth.py`](./api/auth.py). These include:
- An [`authenticated` decorator](./src/api/auth.py#L25)
- A [`/login` endpoint with OAuth redirect to Edge](./src/api/auth.py#L41)
- A [`/authorize` endpoint](./src/api/auth.#L57) which will be the `redirect_uri` for handling Edge OAuth

## A Quick Note On Security Requirements

Edge provides your application with the identity of the Edge user requesting
access to your app, in the form of a user ID, typically an email address.  Edge
guarantees that the user ID is genuine; in other words, the user is who they say
they are.  This is _authentication_.

Depending on your app's security model, you would likely also need to handle
_authorization_.  Most apps won't want to simply allow any authenticated user to
access information, because not every authenticated user may belong to the
business unit or team working with the app.  Typically you will perform
additional _authorization_ checks before allowing an authenticated user access.  

As an example, you might have a list of authorized user IDs in a database, or
even in a config file that the app can load on startup. There is a
[convenient location](./src/api/auth.py#79) in this example's source code where
you can add an authorization check.  The stub implementation that ships with
this example will allow access by any registered Edge user.

## Accessing The Application

Once your application has been deployed using the configuration provided by Edge, you can
click on the *Edge External App Demo, v1.0.0* tile. This will take you to your deployed
web app. If you click the Login button on the example application, it will perform a login
using Edge.

 ## Running the Application Locally

To perform local development on this application without Edge integration, you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager

First, you will need to create an EDM environment named `dev_env` and install some dependencies.

```commandline
edm install -e dev_env --version 3.8 -y install authlib "flask>2" gunicorn requests && \
edm run -e dev_env -- python -m pip install Flask-Session
```   

Once you have created the `dev_env` environment, you may activate it with:

```commandline
edm shell -e dev_env
```

To build the application, use:

```commandline
python -m ci build
```

You can run this application in debug mode without Edge authentication integration using:

```commandline
python -m ci watch backend
```
