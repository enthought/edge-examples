# Edge Core Examples

## About

This GitHub repo holds working examples of apps supported by Enthought Edge.

Each example is a standalone container that inherits from `edm-centos-7`.

The examples are self-contained, with their own README.md and "ci" module that
contains build commands.  For new users, the recommended workflow for
development is:

* Make a copy of the example files.
* Following the instructions in the README file, get to the point where the
  example app is working locally.
* Publish the example (possibly with minor changes to the config, such as adding
  an image name that matches your Docker repository).
* Ensure you are able to launch the app in Edge.
* Modify your copy of the example as desired.
