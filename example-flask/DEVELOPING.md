# Development Guide

## Bootstrapping

Before starting, ensure you have the following installed:

* [Docker](https://docker.com)
* [Node JS](https://nodejs.org)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

After insuring these are installed, run ``npm install -g configurable-http-proxy``
to install a proxy module needed by JupyterHub. 

Then, create an EDM environment for local development:

* Run ``python bootstrap.py``.  This will install a number of packages, and 
  finally print the name of your new EDM environment.

* Activate the environment, by running ``edm shell -e <environment name>``.


## Overview of files in this example

This example contains:

* A **"ci" module**, whose commands are detailed in the following sections.  This
  module provides everything needed for local development and running e.g.
  tests in GitHub Actions.

* A **config.py** module, with various settings including package dependencies.

* A **"src" directory**, containing your application's source code.  This means
  _all_ source code, including Python, React, etc., and any startup scripts or
  templates that will find their way into your app's Docker image.

* A **Dockerfile**, which specifies how the Docker image for your app should
  be built.  This references various files from your source tree, and some
  artifacts which are built by the "ci" module.

* Other various configuration and settings files.


## The "ci" module commands

This example directory contains a "ci" module, which you can use to perform
development tasks, either locally or in GitHub Actions.

There are three command groups, for the following purposes:

* Local development commands, accessed via ``python -m ci dev``, are used
  during the development of the app itself.  These run the app (and its tests)
  in a subprocess, without Docker or Edge.

* Container commands, accessed via ``python -m ci container``, are used for
  building, testing, and publishing your app as a Docker image.  These require
  that Docker is installed on the local system.

* The "preflight" command group, accessed via ``python -m ci preflight``,
  allows you to test your app against a local JupyterHub process before
  publishing to Edge.  This is important as it will allow you to catch
  problems with e.g. your app's authentication system, before publishing to
  Edge.


## Local development tasks

The ``python -m ci dev run`` and ``python -m ci dev test`` commands,
respectively, will run and test your app outside of Docker and Edge.  These
run very quickly, and so are suited to day-to-day development.


## Docker-container tasks

These cover all aspects of the "Dockerization" process: packaging your app
into a Docker image, running it locally, testing, and finally publishing to
a registry like Quay.io or Docker Hub.

### Build

To start with, you can build a Docker image containing your app by running
``python -m ci container build``.  This will perform the following tasks:

* Construct an EDM data bundle ("zbundle") with your app's Python dependencies.
  These are defined in "config.py".
* Perform any build tasks, such as running ``npm`` to package up React code.
* Finally, uses the Dockerfile to combine the various parts
  (source files, zbundle, npm-generated archives) together into a Docker image.

### Run

Once your Docker image has been built, you can the app as a container via
``python -m ci container run``.  The app will start on http://127.0.0.1:8888.
Note that other URLs or IP addresses may be printed to the console during
app startup, and should be ignored.

### Test

You can run ``python -m ci container test`` to make sure your app provides the
various interfaces expected by Edge.  This is a good check to reduce the risk
that your app won't work when deployed to Edge.

### Publish

Running ``python -m ci container publish`` will push your app to the appropriate
Docker registry.  Be sure you are logged in (``docker login <registry>``)
before attempting.  **Before publishing, you should run preflight checks as
described later in this document**.

### Bundle rebuild

During the Docker image build, a .zbundle file is constructed with dependencies.
This is expensive to create, so it isn't regenerated each time the
``container build`` command is run.  If your dependencies change, you should
rebuild the bundle file by running ``python -m ci containers generate_bundle``.


## Preflight tasks

These should be used as a "final check" before publishing to Edge.  They will
test your app against a local JupyterHub instance.

Run ``python -m ci preflight run`` to run JupyterHub.  You can log in at
http://127.0.0.1:8000.  Enter the username "edge" and the password "password".

To run the preflight check in an automated way, do 
``python -m ci preflight test``.  This can be e.g. incorporated into a 
GitHub Actions workflow.


## edge_settings.json

You will notice an edge_settings.json.example file in this example's root.
During development, it is often convenient to have a genuine EdgeSession
object for e.g. interacting with the Edge file system.  To make an EdgeSession
available in your app during development, fill in the fields in this file
and rename it to "edge_settings.json".  The "ci" module will pick up the
information and set the appropriate environment variables when your app runs.

**Please be careful not to check edge_settings.json into source control, and
do not copy it into your Docker image.**  When running in the real Edge
system, the EdgeSession object can be created automatically using the
token, etc., of the user who launched the app.  This information is scraped
from the environment when you call ``EdgeSession()`` constructor.


## Environment variables

Within your app, you have access to a number of environment variables which
may be useful for the development process:

APP_VERSION: In local mode, this is a string with the Docker image name + tag.
**When running in the real Edge system, this variable will not be defined.**

NATIVE_APP_MODE: When running with ``python -m ci dev``, this will be set to
"dev".  When running with ``python -m ci container``, this will be set to
"container".  **When running in the real Edge system, this variable
will not be defined.**  In general, you should try to minimize logic that depends on
this variable, to avoid unexpected behavior when moving from local development
to production.


## Managing EDM and Pip dependencies

In config.py, you can specify both _local development_ dependencies, which
will be used in your bootstrap.py-build development environment, and you
_application dependencies_, which will be installed into your Dockerfile.
By default, both will use the list of Deployment Server repositories given
in your ``~/edm.yaml`` file, along with any credentials in that file.  You
can select a different ``edm.yaml`` file using the ``--edm-config`` option
to commands like ``python -m ci container build``.

If you need to install packages from Pip, you can do so in config.py for
local development dependencies.  For application dependencies, you should
put the Pip command in your Dockerfile.  We recommend something like this:
```
RUN edm run -e <env name> -- pip install --no-cache-dir <requirements>
```
Using ``--no-cache-dir`` will reduce the size of the Docker image.


## Registering versions of your app with Edge

Once you have published
As a quick reminder, in Edge, there is a distinction between an _app_ and an
_app version_.  Your organization administrator can define an _app_, and then
developers are free to register _app versions_ associated with that app.  This
ensures that org administrators have full control over what shows up on the
dashboard, but gives developers freedom to publish new versions by themselves.

You can register a new app version by logging in to Edge, going to the
gear icon in the upper-right corner, and navigating to the app in question.
There is a form to fill out which asks for the version, Quay.io or DockerHub
URL for the image, and some other information.

You can also register your app version programmatically.  This is particularly
convenient during the development process, for automated builds.  A general
example looks like this, for an app whose ID is ``my-app-id``:

```
from edge.api import EdgeSession
from edge.apps.application import Application
from edge.apps.app_version import AppKindEnum, AppVersion
from edge.apps.server_info import ServerInfo

# Create an Edge session
edge = EdgeSession(
    service_url="https://edge.enthought.com/services/api",
    organization="<YOUR_ORGANIZATION>",
    api_token="<YOUR_EDGE_API_TOKEN>"
)

# Register the application version
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
version = AppVersion(
    app_id="my-app-id",  # Specified when the app is created
    version="1.0.0",  	 # or whatever version you have
    title="My Application Title",
    description="This Is An Example Edge Application",
    icon=ICON,
    kind=AppKindEnum.Native,
    link="quay.io/enthought/YOUR_IMAGE_NAME_HERE:TAG",
    recommended_profile="edge.medium"
)
edge.applications.add_app_version(version)
```