# Edge examples gallery

![Screenshot of the Flask/React example](.dev/images/example-flask.png)

This GitHub repo holds working examples of apps which run on Enthought Edge.

Each example is self-contained, with its own README.md and "ci" module that
contains build commands.  For new users, the recommended workflow for
development is:

* Make a copy of the example files.
* Following the instructions in the README file, get to the point where the
  example app is working locally.
* Publish the example (possibly with minor changes to the config, such as adding
  an image name that matches your Docker repository).
* Ensure you are able to launch the app in Edge.
* Modify your copy of the example as desired.


## Basic Example

It's recommended you start here.  The Basic Example is a simple Flask
"Hello World" app, which shows how to build your application's Docker image,
run and debug it locally, and finally publish it to Edge.  

Using the Edge API (EdgeSession) within the app is also demonstrated.  This
allows you to access files and data connectors stored in Edge, directly from
your application code.


## Advanced Examples

These are somewhat more complicated, because each demonstrates the use of
a particular feature or framework, for example Panel or Streamlit.  See the
README.md for each example for details.



