# Tools

This folder holds tools which are useful during the application development
process.


## "Preflight" check utility

The ``preflight.py`` script is a self-contained utility to check your
application's compatibility with Edge.  It will launch your app inside a
local JupyterHub instance, and run a variety of checks including:

* Whether the application launches correctly.
* Whether the application's root page is accessible.
* Whether the application correctly handles authorization (this is automatic,
  if you are using the ``edge-native-base`` image in your Dockerfile).

### Before you begin

Before starting, ensure you have the following installed:

* [Docker](https://docker.com)
* [Node JS](https://nodejs.org)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

Then, run ``npm install -g configurable-http-proxy`` to install a proxy module
needed by JupyterHub. 

### Using the preflight utility

To get started, run ``python bootstrap.py`` to install dependencies in a
separate EDM environment, and activate that environment.

Then, run ``python preflight.py <image_name>`` where ``<image_name>`` is the
full name of a Docker image, in the form ``example.com/foo/bar:tag``.  You
may need to pull the image first, with ``docker pull``, if it was not built
locally.

In case one of the checks fails, the script will produce log files for both
the application and the JupyterHub server.  Default names for these are
"edge-app-log.txt" and "edge-hub-log.txt" in the current working directory.
Run ``python preflight.py --help`` to see how to change these.

In addition to printing the check status to the console, the script will exit
with an nonzero exit code on failure.  This makes it easy to integrate with a
GitHub Actions workflow.