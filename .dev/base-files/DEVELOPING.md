# Development Guide

## The "ci" module commands

This example directory contains a "ci" module, which you can use to perform
development tasks, either locally or in GitHub Actions.

Before you start, ensure you have run "bootstrap.py" to create your local
EDM development environment.  You should then activate the local development
environment, using ``edm shell -e <environment name>``, before running the
``ci`` module commands.

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
run very quickly, and so are suited to day-to-day development,.

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
* Finally, follow instructions in your Dockerfile to combine the various parts
  (source files, zbundle, npm-generated archives) together into a Docker image.

### Run

Once your Docker image has been built, you can the app as a container via
``python -m ci container run``.  The app will start on http://127.0.0.1:8888.
Note that other URLs or IP addresses may be printed to the console during
app startup, and should be ignored.

#### Test

You can run ``python -m ci container test`` to make sure your app provides the
various interfaces expected by Edge.  This is a good check to reduce the risk
that your app won't work when deployed to Edge.

#### Bundle rebuild

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