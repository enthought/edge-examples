# React example

This example shows how to develop an application for Edge using the React
library.  You can read more about React at https://react.dev/.

One of the most exciting features of Edge native applications is the ability
to do long-running computation, without leaving your app.  Because each user
has their own dedicated container, doing heavyweight computation is as easy
as creating a new thread.

This example uses the OpenCV library to detect faces in uploaded images.
Upon upload to the React front-end, a compute task is launched inside the
backend process.  When the compute task finishes, the image is updated to
display bounding boxes around the features that match.  See "app.py" in the
src/application folder for details.

Tips for using React (and Flask) when building an Edge native app:

* The "prefix" (URL) of your app changes depending on which user is running
  the app.  See "app.py" for how to retrieve this value.  You can then pass it
  down to React via a template file.  See the frontend/templates/index.html file
  for an example of how to do this using a script tag.  This value can be used
  in turn, on the React side, to compute the right URL for use with "fetch".

* Don't "block" a Flask callback waiting on compute.  Instead, spin off a
  thread to manage it, and use e.g. polling to update the frontend state once
  the compute job is finished.

* You should run with a single gunicorn worker.  If you want to run subprocesses,
  avoid forking the process, and use spawn instead.


## Before you begin

Before starting, ensure you have the following installed:

* [Docker](https://docker.com)
* [Node JS](https://nodejs.org)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

Then ensure your ``edm.yaml`` file lists ``enthought/edge`` as an egg
repository.  This will be necessary to use EdgeSession in the example.


## Quick start

1. Run ``python bootstrap.py``.  This will create a development environment
   and activate it, dropping you into a development shell.

2. From within the development shell, build the example by running
   ``python -m ci build``.  This will produce a Docker image.

3. Run the Docker image via ``python -m ci run``.  The app will serve on
   http://0.0.0.0:9000 in a local development mode.


## Modifying the example for your use case

Please note these are the minimal changes necessary to make the example your
own.  Depending on your use case you may wish to add additional "ci" commands,
install different items in the Dockerfile, etc.

* In ``ci/__main__.py``, change the constants IMAGE, VERSION, and
  APP_DEPENDENCIES as appropriate.
* In ``bootstrap.py``, consider changing the name of the development
  environment (ENV_NAME) to avoid conflicts with other examples.


## Publishing your app

1. Ensure you are logged in (via ``docker login``) to DockerHub, Quay.io, or
   another Docker registry.

2. Run ``python -m ci publish`` to push your app's image to the registry.

Once you have published your Docker image, you are ready to register that
version of your app with Edge.

As a quick reminder, in Edge, there is a distinction between an _app_ and an
_app version_.  Your organization administrator can define an _app_, and then
developers are free to register _app versions_ associated with that app.  This
ensures that org administrators have full control over what shows up on the
dashboard, but gives developers freedom to publish new versions by themselves.

The easiest way to register a new app version is by logging in to Edge, going
to the gear icon in the upper-right corner, and navigating to the app in
question. There is a form to fill out which asks for the version, Quay.io or
DockerHub URL for the image, and some other information.

It is also possible to register app versions programmatically, for example
from within a GitHub Actions workflow.  See the example at the end of this
README.


## Getting EdgeSession to work in development

When you run your app on Edge, you can create an EdgeSession object simply by
calling the constructor (``mysession = EdgeSession()``).  This works by
collecting environment variables set by Edge when the container is launched.

When developing locally, it's also convenient to have an EdgeSession.  You
can get the "ci" module to inject the appropriate environment variables, so
that your ``EdgeSession()`` call will work with ``python -m ci run``.  

To do so, follow this procedure:

* Copy the "dev_settings.json.example" file to "dev_settings.json".
* Define EDGE_API_SERVICE_URL in that file.  The typical value here is
  ``"https://edge.enthought.com/services/api"``.
* Define EDGE_API_ORG in that file.  This is the "short name" displayed in
  the URL bar when you log into an organization, for example, ``"default"``.
* Define EDGE_API_TOKEN.  You can get one of these from the ``My Profile``page
  in the Edge UI.

Be sure *not* to check the "dev_settings.json" file into source control, as it
contains your API token.


## Routes and prefixes

This example is designed to be run next to a reverse proxy provided by Edge, 
that handles routing, along with the more complicated parts of talking to 
JupyterHub (for example, handling the OAuth2 connection process).

Edge will serve your app under a URL prefix which is set at runtime, and
contains values like the current user name and app name.  This prefix is
passed down to your app in the environment variable JUPYTERHUB_SERVICE_PREFIX.
Your app will need to respond to HTTP requests that include this prefix.  

In practical terms, if you want to serve your app's home page as "index.html",
you should use a Flask route like ``@app.get(PREFIX + "index.html")``.

The JUPYTERHUB_SERVICE_PREFIX value may or may not be set when running in
local mode.  To be safe, you should fall back to a value of "/" if it's not
found.


## Viewing console output

When running with ``python -m ci run``, the app's output will be displayed
on the console where you launched it.

## Guidelines for your Dockerfile

Edge will run your app next to a built-in reverse proxy, which allows
you to skip a lot of work in the development process.  This includes stripping
the prefix from requests, handling the OAuth2 login flow, pinging JupyterHub
for container activity, and more.  But, there are a few guidelines you will
need to follow in your own Dockerfile.

* Your app should bind to ``127.0.0.1``, *not* ``0.0.0.0``, and it should serve
  on port 9000.  The Edge machinery will respond to requests on port 8888 and 
  forward them to your app.


## Publishing versions from CI (e.g. GitHub Actions)

You can register your app version programmatically.  This is particularly
convenient during the development process, for automated builds.  A general
example looks like this, for an app whose ID is ``my-app-id``:


```
from edge.api import EdgeSession
from edge.apps.application import Application
from edge.apps.app_version import AppKindEnum, AppProxyKindEnum, AppVersion
from edge.apps.server_info import ServerInfo

# Create an Edge session.
edge = EdgeSession(
    service_url="https://edge.enthought.com/services/api",
    organization="<YOUR_ORGANIZATION>",
    api_token="<YOUR_EDGE_API_TOKEN>"
)

# Register the application version.

# Icon is a base64-encoded PNG.  
# It should be square, any size; 64x64 or 128x128 are common.
ICON = (
    "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAk1BMVEUAAA"
    "AMfIYAdnwAdnwAd3wAc3kAdntYsb8AdnwAdn0AdXwAdXsAd30Ad3xYsb8A"
    "d30AdntYsL8Ad30AdnsAd30AdnwAd3wAd30AdnxYssBYsb5Ysr9Zs70Adn"
    "tYsr9Ysb9Ysb9Ysr8AdnxXs75Ysb4AdXsAd3wAdnxYsb8AeoAAfYMAf4Vb"
    "t8Zfv84Ad31ixtVevMuy+odXAAAAJ3RSTlMABPr88Shd+4pmkXyDbfB0Xy"
    "dWTy0h9TLnkYv+IJmX9uigNzOIf5LOQ2WlAAAC/ElEQVR42sXX7VLiMBiG"
    "4aTBDwQVEJSPXdkF3dAi1fM/uoXp7DyzIzHEm7bvT6Dc16SlDQbObG5anf"
    "nHx4tpcea7q6sdWQPeXyyIgPc3+7nazQwY3N8sWhLM9uu/+Sd4NmBQvxog"
    "YH0g4P2qLMFvAwb0WxE8q9+CwJqX96W6muV7U9fB8NfbsRV4u1ubhubHQf"
    "C5PzQNjZXg/741dY8EdxKAPhTQPhfQPhfQPheQPhcM9wLa54KG+jYoCPZt"
    "M4Llspn+KlRZr0PvrM7Z/7m9DHVCr19ub87Zd4UEX436hZeA9zPnJTix7z"
    "IJcN97CU7tey8B70twev9Mgj+HvgQJ/fMIbqq+BCl9CXhfgpS+BLwvQUpf"
    "At6XIN7nAvWTBOpDgfppgm6uPhGonyaw00LHAIH6qYLJNA8KeD8usF8Irk"
    "E/SdChAvXbEajfjkD9dgTqtyNQv0XB9aFPBRcRAexzQXo/q1MQ77uyqHEN"
    "4v2smPby0qUKHoOC1H7eGZtB4VMF47AgtX+hrU4Ngmj/cWzs+QU2rW/qFc"
    "T7lSA/o6BvbEq/+rpRuuApiwvi/doE0X72pA/VJYj36xXE+7UL+sf7Tn0s"
    "WPncBQTh51/Z0fV3oiDvBtegU/rQ/eC1OIpz5XRirEkQOFfch/8ulEfNru"
    "gZcx8QVI+AuECnoGtM8NEc6N8aY0OC7ESB+qdvDdS33xQ8aH9A+0igfj74"
    "Zh8K9BMEfSxwPgd9KKj6o8S+V58KaJ8LXJk/gD4WeM/6XMD6XDCC558LYJ"
    "8LYJ8LQB8IYJ8IeD9+eG9LBPH7PxTgPhbQPhfwPhek932gDwTRfnjLyAW0"
    "zwW8H5+IAPa5gPa5gPa5gPa5gPa5gPa5gPa5gPa5gPa5APa5gPW5YDJBfS"
    "6YTkmfC1xZukb6NiiAfS4AfSAAfSQoHOpzwes2Q30+fQla6VsJQB8LeJ8L"
    "wv0B6AMB6AMB6HMB7XMB7XMB7XMB7XMB7XMB7XMB7XMB7XMB7XMB7XMB7H"
    "NBjvpccH0L+38B6kvWH2wXIe8AAAAASUVORK5CYII="
)
version = AppVersion(
    app_id="my-app-id",  # Specified when the app is created
    version="1.0.0",  	 # or whatever version you have
    title="My Application Title",
    description="This Is An Example Edge Application",
    icon=ICON,
    kind=AppKindEnum.Native,
    framework=AppProxyKindEnum.React,
    link="quay.io/<YOUR_ORGANIZATION>/YOUR_IMAGE_NAME_HERE:TAG",
    recommended_profile="edge.medium"
)
edge.applications.add_app_version(version)
```