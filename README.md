# Edge Examples

Welcome to the Edge examples repo!  This GitHub repo holds working examples of
apps which run on Enthought Edge.  As an Edge developer, you are free to make
copies of the apps here and modify them to add your own functionality.

Table of Contents

* [Suggested Development Workflow](suggested-development-workflow)
* [List of Examples](list-of-examples)
* [Using the edge-native-base Docker image](using-the-edge-native-base-docker-image)
* [Security when not using edge-native-base](security-when-not-using-edge-native-base)

## Suggested Development Workflow

1. Make a copy of the example you're interested in.

2. Ensure you are able to build and run the example, by following the README
   file in the example's folder.  This will help find problems with your
   development environment, for example missing tools or packages, before you
   start developing.

3. Update the app name and Docker repository information in config.py, to
   put in your own information.

4. Publish your app and register it with Edge.  The example's README will have
   information on how to do this.  More information is also available in the
   [online Edge documentation](https://docs.enthought.com).

5. Log into Edge, and ensure you can launch the app.

6. Modify the example to add your desired functionality.

## List of Examples

### Example 1: Flask/React

Located in the [example-flask](example-flask) folder.

This is a simple image-recognition demo, which uses a Flask backend and React
frontend.  It leverages the OpenCV library to detect faces in an uploaded
image.

![Screenshot of the Flask/React example](.dev/images/example-flask.png)

### Example 2: Dashboard

Located in the [example-dashboard](example-dashboard) folder.

This is a smaller example, demonstrating how to build a minimal "dashboard"
app with plots, graphs, and other widgets.

![Screenshot of the Dashboard example](.dev/images/example-dashboard.png)

### Example 3: Plotly Dash

Located in the [example-plotly-dash](example-plotly-dash) folder.

This demonstrates how to use [Plotly Dash](https://plotly.com/dash/) to build
a visualization-based science app.

![Screenshot of the Plotly Dash example](.dev/images/example-plotly-dash.png)

### Example 4: Panel

Located in the [example-panel](example-panel) folder.

This app demonstrates how to use [Panel](https://panel.holoviz.org/) to build 
an Edge app.

![Screenshot of the Panel example](.dev/images/example-panel.png)

### Example 5: Streamlit

Located in the [example-streamlit](example-streamlit) folder.

Demonstrates the use of [Streamlit](https://streamlit.io/) to build Edge apps.

![Screenshot of the Streamlit example](.dev/images/example-streamlit.png)

### Externally-Hosted App

Located in the [example-external](example-external) folder.

This shows how to add a tile to the Edge workbench, which points at a service
running outside of Edge.  It also demonstrates how to use Edge as an
authentication backend for your app.

## Using the edge-native-base Docker image

To ease development, the Edge team provides a base Docker image you can use
as a basis for your app.  This includes a recent copy of EDM, and additionally
will perform all functions related to OAuth2 authentication.

The full name of the image is ``quay.io/enthought/edge-native-base``.

If you use this image as the base for your Dockerfile, your app does not need
to perform authentication or authorization checks.  If someone is able to
call your app's API, you can have confidence that they are they are the same
authorized Edge user who launched the app.

Here are some things to keep in mind, as you work with ``edge-native-base``:

* In your Dockerfile, you should pin to a particular version, in other words
  do ``FROM quay.io/enthought/edge-native-base:1.0.0``, rather than e.g.
  ``FROM quay.io/enthought/edge-native-base:latest``.

* Install any EDM environments, application files, etc., in the
  ``/home/app`` home directory.

* Do not override the ``CMD`` of the base image; instead, place your app's
  startup script at ``/home/app/startup-script.sh``.  See the examples for
  what goes in this script.

* Your app should serve on port 9000.  The ``edge-native-base`` image will
  automatically proxy this to port 8888, which is what Edge expects.

* In rare cases, you may need to place an nginx template file in ``/opt/nginx/``
  to help the base image understand how to proxy your app.  See the example
  code for details, or reach out to the Edge team for help.

## Security when not using edge-native-base

If you choose not to use the edge-native-base image, your app will need to
handle the OAuth2 flow with Edge itself.  Reach out to the Edge team for
more information.  **If you do not use edge-native-base, and do not handle the
OAuth2 flow yourself, your app will be open to the world without any
security.**