# Externally-Hosted App Example

The rest of the examples in this repo are for _native apps_, meaning each user
gets their own dedicated backend server managed by Edge.  However, it's still
useful to integrate Edge with regular multi-user web applications.  We call
these _externally-hosted apps_, since they are deployed and managed outside of
Edge.

Edge provides two important mechanisms for integrating with externally-hosted
apps.  First, you can register such an app on the Workbench, so that users
can go straight to it after logging in.  Second, you can set up the
externally-hosted app's login flow to use Edge as a source of information on
the user, via the industry-standard OAuth2 protocol.


## Overview

This folder contains a minimal Flask application that demonstrates both
mechanisms, along with example Terraform code you can use to deploy the app
in a Kubernetes cluster.

Here is the general outline; each step is explained in more detail below:

1. Set up your development environment, and gather necessary information for
   later steps.
2. Write your application, paying particular attention to your end of the OAuth2
   workflow.  This folder already contains a working demo application; you
   should start by trying to get it to work unmodified.
3. Register the app with Edge.  This will create a tile on the Workbench, and
   will provide some OAuth2-related secrets you'll need when deploying the app.
4. Deploy the application, using the example Terraform code.
5. Log into the application, and verify that it works properly.


## 1. Set up your development environment, and gather information

Before starting, ensure you have the following installed:

* [Docker](https://docker.com)
* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 
* Deployment-time dependencies listed in the [deploy](./deploy/README.md) folder.

Collect the following information:

* The hostname under which your app will be deployed.  For this example, we will
  use "https://edge-external-app-demo.edge-dev.enthought.com".
* A Docker repository and related username/password.  For this example, we will
  use "quay.io/enthought/edge-external-app-demo".

To get started with local development, run ``python bootstrap.py``.  This will
create a local development environment and activate development shell.  From
within this shell you can run various "ci" module commands.

To build the application, use:

```commandline
python -m ci build
```

You can run this application in debug mode without Edge login integration using:

```commandline
python -m ci watch
```


## 2. Application code requirements

Edge will handle OAuth for your external web application. In this example,
we will provide `client_id`, `client_secret` and `redirect_uri` to the
[`authlib`](./src/app.py#L31) library.  These three pieces of information will
come from the Edge registration process in step 3.

The requirements for login in this example Flask application are handled
in [`api/auth.py`](./src/api/auth.py). These include:
- An [`authenticated` decorator](./src/api/auth.py#L25)
- A [`/login` endpoint with OAuth redirect to Edge](./src/api/auth.py#L41)
- A [`/authorize` endpoint](./src/api/auth.py#L57) which will be the 
`redirect_uri` for handling Edge OAuth

Finally, keep in mind the Edge login flow grants your application basic
identity information regarding a user, for example a user ID, typically an
email address.

Depending on your app's security model, you would likely also need to provide
a more detailed authorization process. Most apps won't want to simply allow any 
user to access information, because not every Edge user may belong to the
business unit or team working with the app.  Typically you will perform
additional checks before allowing an authenticated user access.  

As an example, you might have a list of authorized user IDs in a database, or
even in a config file that the app can load on startup. There is a
[convenient location](./src/api/auth.py#79) in this example's source code where
you can add an authorization check.  The stub implementation that ships with
this example will allow access by any registered Edge user.


## 3. Registering the app with Edge

We will register the app with Edge before deploying it.  This may seem backwards,
but it's necessary since we need the OAuth2 information (client_id, client_secret,
redirect_uri) in order to deploy the app.  That information comes from the
Edge registration process.

As a quick reminder, in Edge, there is a distinction between an _app_ and an
_app version_.  Your organization administrator can define an _app_, and then
developers are free to register _app versions_ associated with that app.  This
ensures that org administrators have full control over what shows up on the
dashboard, but gives developers freedom to publish new versions by themselves.

Once your administrator has created the _app_, you can make a new _app version_
by logging into Edge, going to the "gear" icon, and navigating to it.
Click "Create Version" and fill out the form, being sure to set "Kind" to
"Externally Hosted App".  For the "Link", you should provide the hostname
from step (1).

Once your app version is created, you will need to create the OAuth2
information.  This has to be done in code, at the moment.  The easiest way
to do this is from within a Jupyter notebook within Edge.  (You are also
free to do so from your laptop, or e.g. in a GitHub Actions workflow; all you
need is an EdgeSession object).

The code itself is very simple.  You'll need the hostname from Step 1:

```python
endpoint = "<your example hostname from step 1>/authorize"
result = edge.applications.register_oauth_client(app.app_id, endpoint)
```

The ``result`` variable here will have the OAuth2 information needed to
deploy the app.  It looks something like this:

```python
{'client_id': 'service-edge-app-default-edge-external-app-demo',
 'client_secret': 'RANDOM_CLIENT_SECRET',
 'redirect_uri': 'https://edge-external-app-demo.edge-dev.enthought.com/authorize'}
 ```

## 4. Deploying the app

Follow the instructions in the [deploy folder README](./deploy/README.md).


## 5. Accessing The Application

Once your application has been deployed using the configuration provided by
Edge, you can click on the app tile on the Workbench. This will
take you to your deployed web app.  If you click the Login button on the
example application, it will perform a login using Edge.


