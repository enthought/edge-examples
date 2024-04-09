# Tools

This folder holds tools which are useful during the application development
process.


## "testrun" check utility

The ``testrun.py`` script is a self-contained utility to run your application and
do a variety of checks including:

* Whether the application launches correctly.
* Whether the application's root page is accessible.

### Before you begin

Before starting, ensure you have the following installed:

* [Docker](https://docker.com)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

### Using the testrun utility

To get started, run ``python bootstrap.py`` to install dependencies in a
separate EDM environment, and activate that environment.

Then, run ``python testrun.py <image_name>`` where ``<image_name>`` is the
full name of a Docker image, in the form ``example.com/foo/bar:tag``.  You
may need to pull the image first, with ``docker pull``, if it was not built
locally.

In case one of the checks fails, the script will produce a log file for
the application.  The default name for this log is "edge-app-log.txt" in the 
current working directory.
Run ``python testrun.py --help`` to see how to change this.

In addition to printing the check status to the console, the script will exit
with a nonzero exit code on failure.  This makes it easy to integrate with a
GitHub Actions workflow.
