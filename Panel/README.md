# Panel example

This example shows how to develop an application for Edge using the Panel
library.  You can read more about Panel at their official site: 
https://panel.holoviz.org/.


## Before you begin

- **Try the new Edge CLI tool:** If you prefer a streamlined, automated
workflow, use the [Edge CLI](#develop-panel-app-example-with-the-edge-cli). This tool simplifies the process of creating,
managing, and publishing Edge applications.

- **Manual setup:** For a more hands-on approach, follow the steps in this
section. This involves configuring your development environment and Docker
manually.

## Required tools for the manual setup:

Ensure you have the following installed:

* [Docker](https://docker.com)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

Then ensure your ``edm.yaml`` file lists ``enthought/edge`` as an egg
repository, along with ``enthought/free`` and ``enthought/lgpl``.  This will be
necessary to use EdgeSession in the example.


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
    framework=AppProxyKindEnum.Panel,
    link="quay.io/<YOUR_ORGANIZATION>/YOUR_IMAGE_NAME_HERE:TAG",
    recommended_profile="edge.medium"
)
edge.applications.add_app_version(version)
```

# Develop Panel app example with the Edge CLI

The Edge CLI is a command-line tool that allows you to interact with the Edge 
platform. You can use the Edge CLI to create, manage, and deploy applications on
Edge.

## Installing the Edge CLI

To install the Edge CLI, you need to have the Enthought Deployment Manager (EDM)
and with that you can install the `enthought_edge` client and `edge_cli`:

```
$ edm shell
$ edm install enthought_edge edge_cli
```

Then you can test the CLI with:

```
$ edge
```

## Step 1: Initialize a new application

Before initializing an application, **ensure Docker is installed and running on your machine**. 
The Edge CLI relies on Docker to manage the application's containerized
environment.

**Prerequisite: Docker installation**

You can install Docker by following the official instructions for your operating
system:

- **For macOS and Windows:** Use [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **For Linux:** Use the appropriate package manager, or follow this [guide](https://docs.docker.com/desktop/install/linux/).

Once Docker is installed, ensure it is running before proceeding with the Edge
CLI commands.

In a terminal, execute the edge command to initialize a new application:

```
$ edge app init
```

This will log you into Edge (if necessary) and prompt you for the following:

```
? Application ID: my-app
? Create application in which organization? Default organization
? Application framework? Holoviz Panel
Do you want to create new application "my-app"? [Y/n]:
```

Answer `Y` to create the application. This will create a new directory with the
name of the application ID in the current directory, download the example
application for the chosen framework into that directory, create an EDM
virtual environment, and create an application record in Edge.

Further `edge app` commands are performed from within the application
directory:

```
$ cd my-app
```

## Step 2: Build and test

You can build the application with:

```
$ edge app build
```

This prompts you for the version to build as, with version `1.0.0` as the
initial default:

```
? Build to version: 1.0.0
```

If you override this default, it will build to the new version number and that
becomes the new default working version.

Once built, you can do a basic "smoke test" with:

```
$ edge app check
```

This will launch the application, ensure it can be communicated with, then
shut it down again.

If you want to interact with the application manually use:

```
$ edge app run
```

This launches your application where it can be found in your web browser
at `http://127.0.0.1:9000/`.  Once you are done, you can shut it down with
`Ctrl-C`.

## Step 3: Publish the application

Before publishing an application, ensure that:

1. You have a **developer license** for the Edge platform.
2. You have been assigned the **developer role** within your organization.

**Note:** Without both a developer license and the appropriate role, you will
not be able to publish applications. If you encounter permission errors during
publishing, please contact your organization's administrator to verify your
access level.

Once your application is built (as described in **Step 2**), you can publish it
by running the following command:

```
$ edge app publish
```

This will push the application to the Enthought quay repository and create an
Application Version record in Edge. Once the application is successfully
published, it can be launched from the Edge Workbench like any other native
application.

## Other commands

You can check the full set of published versions using:

```
$ edge app versions
```

To have the application's dependencies available for further operations,
enter its virtual environment:

```
$ edge app shell
```

To rebuild the application's EDM environment:

```
$ edge env build
```

See the full list of application commands with:

```
$ edge app --help
```

Run any given command in verbose mode for debugging:

```
$ edge app --verbose <command>
```

## Handling Application Compatibility in Edge CLI

When working with the new Edge CLI alongside an older installed application, you
might encounter compatibility issues during the build process. These issues
arise because the configuration file format has changed, and the new CLI is
designed for the updated format. Follow the steps below to resolve the issue:

### Instructions

1. Trigger the Build

Run the following command to build your app:

```
$ edge app build
```

If your app's configuration is incompatible with the new CLI, the command will
fail with a message indicating the need to upgrade.

2. Upgrade the App Configuration

Upgrade the application's configuration to the new format using:

```
$ edge app upgrade
```

This command updates the application's configuration file to match the
requirements of the new Edge CLI. If the configuration is already compatible,
the command will exit cleanly, confirming that no further changes are necessary.

3. Rebuild the App

Attempt the build again:

```
$ edge app build
```

This time, the build should succeed, as the configuration has been updated to
ensure compatibility with the new CLI.
