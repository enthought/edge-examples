# Externally-Hosted App Example

This folder contains a Flask + React application that showcases how to
integrate an external web app with Edge, by using JupyterHub as the OAuth2 provider.

## Pre-Requisites

To integrate your external web app with Edge, you need to know the hostname of where
your app will be hosted. For this demonstration, we will integrate the application deployed
to [`https://edge-external-app-demo.platform-devops.enthought.com`](https://edge-external-app-demo.platform-devops.enthought.com)


## Application Requirements

Edge handles OAuth for your external web application. The requirements for the authenticating
this Flask application are handled in [`api/auth.py`](./api/auth.py). These include

## Registering Your Application

As an Edge organization developer, you must register your application. From the Analysis
app on Edge, start an Edge notebook and use the code below. Be sure to substitute the
`external_hostname` with your application's hostname.

```python
from edge.apps.application import Application, AppResource
from edge.apps.app_version import AppKindEnum, AppVersion

external_hostname = "https://edge-external-app-demo.platform-devops.enthought.com"

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


app = Application(
            app_id='edge-external-app-demo',
            visible_versions=[],
            visible_auto_add=True,
            max_resources=AppResource(cpu=1, gpu=0, memory=1000000),
            max_global_resources=AppResource(cpu=10, gpu=1, memory=20000000),
        )


version1 = AppVersion(
            app_id=app.app_id,
            version="1.0.0",
            title="Edge External App Demo, v1.0.0",
            description="Demonstration of an external application",
            icon=ICON,
            kind=AppKindEnum.External,
            link=external_hostname,
            profiles={
                "small": AppResource(cpu=1, gpu=0, memory=1000000, shutdown=7200),
                "less-small": AppResource(cpu=2, gpu=0, memory=2000000, shutdown=14400),
            },
            default_profile="small",
            volume_mount_point="/data",
            suggested_volume_size=1,
        )



edge.applications.add_application(app)
edge.applications.add_app_version(version1)

result = edge.applications.register_oauth_client(app.app_id, f"{external_hostname}/authorize")
result
```

The result will be something like this:

```python
{'client_id': 'service-edge-app-default-edge-external-app-demo',
 'client_secret': 'RANDOM_CLIENT_SECRET',
 'redirect_uri': 'https://edge-external-app-demo.platform-devops.enthought.com/authorize'}
 ```



 ## Local Development of this Example

To perform local development on this application without Edge integration, you will need:
- [Docker](https://docker.com)
- [Node JS](https://nodejs.org)
- [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager 

First, you will need to create an EDM environment named `dev_env` and install some dependencies.

```commandline
edm install -e dev_env --version 3.8 -y install authlib "flask>2" gunicorn requests && \
edm run -e dev_env -- python -m pip install Flask-Session
```   

Once you have created the `dev_env` environment, you may activate it with:

```commandline
edm shell -e dev_env
```


## Registering Your Application



```
from edge.apps.application import Application, AppResource
from edge.apps.app_version import AppKindEnum, AppVersion

external_hostname = "https://edge-external-app-demo.platform-devops.enthought.com"

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


app = Application(
            app_id='edge-external-app-demo',
            visible_versions=[],
            visible_auto_add=True,
            max_resources=AppResource(cpu=1, gpu=0, memory=1000000),
            max_global_resources=AppResource(cpu=10, gpu=1, memory=20000000),
        )


version1 = AppVersion(
            app_id=app.app_id,
            version="1.0.0",
            title="Edge External App Demo, v1.0.0",
            description="Demonstration of an external application",
            icon=ICON,
            kind=AppKindEnum.External,
            link=external_hostname,
            profiles={
                "small": AppResource(cpu=1, gpu=0, memory=1000000, shutdown=7200),
                "less-small": AppResource(cpu=2, gpu=0, memory=2000000, shutdown=14400),
            },
            default_profile="small",
            volume_mount_point="/data",
            suggested_volume_size=1,
        )



edge.applications.add_application(app)
edge.applications.add_app_version(version1)


result = edge.applications.register_oauth_client(app.app_id, f"{external_hostname}/authorize")
result
```

## Understanding the OAuth 2.0 flow
    
A single OAuth2 flow generally goes like this:

* A user makes an HTTP request to access your application, i.e. the *OAuth2 client*.
* The user is not logged in, so the client redirects the user to an "authorize" 
  endpoint on the *OAuth2 provider*, with some extra information:
    - the *client id* of your application
    - the *client secret* associated with your application
    - the *redirect uri* on your application to be redirected back to after completion
* The user is prompted to sign in on the OAuth2 provider's page
* After the user is authenticated with the provider, a short-lived record
  called an OAuth2 code is generated by the provider and the user is redirected
  to the OAuth2 client's "redirect uri" with the OAuth code.
* The OAuth2 client receives the code and makes an API request to the provider
  to exchange the code for a real *access token*.
* Once the token is retrieved, the client makes a second API request to the
  provider to retrieve information about the owner of the token (the user).
* Finally, the OAuth2 client stores its own record that the user is authorized
  in a cookie.

In the context of an External Edge Application:
- The **OAuth2 client** is your application
- The **OAuth2 provider** is Edge
- The **client id** and **client secret** are obtained when registering your
  application as an external Edge application.
- The **redirect uri** is an endpoint on your application that handles the
  exchange of an OAuth2 code for an access token.

## Pre-requisites

To build and run the example application you will need EDM, Docker and `npm`
installed and available in your PATH.

You will also need to have the Edge stack running alongside JupyterHub. To get
started, run the below commands while at the root of the Edge project directory:

* Build Docker images: ``python -m ci docker build``
* Start JupyterHub: ``python -m ci jupyter start``
* Launch the stack: ``python -m ci stack up``

## Running the Application

If you are running the application for the first time, you will need to build
the application's Docker image. From within the `external-app-example` directory
run:

```commandline
    python -m ci build
```

Once built, start the application with:

```commandline
    python -m ci start
```

## Deploying the Application

If it's your first time deploying the application, make sure you follow the
steps below as they describe how to install and configure `kubectl` and
the `terraform` CLI:

1. Request that Product DevOps add your username to the `edge-dev` namespace
   module
2. Ask Product DevOps for a kube config file. Configurations are stored in the
   Product DevOps Vault.
3. Install `kubectl`
```bash
brew install kubectl
brew link --overwrite kubernetes-cli # if you have Docker Desktop installed
```
4. Install the [kubelogin](https://github.com/int128/kubelogin) plugin
```bash
brew install int128/kubelogin/kubelogin
```
5. Replace your `~/.kube/config` file with one from Product DevOps
6. Switch to the namespace to `edge-dev`
```bash
kubectl config set-context --current --namespace=edge-dev
```
7. Test your configuration
```bash
kubectl get pods
```
8. [Install](https://learn.hashicorp.com/tutorials/terraform/install-cli) `terraform`

Once you've met the pre-requisites listed above, you may continue with the
deployment of the application.

First, `cd` to the `deploy` directory.

If it's your first time deploying the demo application from your environment,
run:
```bash
terraform init
```

To *deploy* the demo application, run:
```bash
terraform apply
```

To check that your deployment succeded you can run `kubectl describe pod` or 
`kubectl describe deploy`.

You can open the demo app in your browser by going to https://edge-dev.platform-devops.enthought.com/

If you make changes to the deployment files, and you would like to preview
those changes before deploying, run:
```bash
terraform plan
```

Note that both `apply` and `plan` will prompt you for various secrets, those
can be found in the project secrets doc in the project's shared drive. If you
are unsure where that is located, or don't have access to the shared drive,
reach out to the project's Team Lead.

If you make changes to the application and would like to see those changes
reflected in the deployment, build and publish your Docker image
using `python -m ci build` and `python -m ci publish`, and restart your
deployment with:

```bash
kubectl rollout restart deploy edge-example-app
```

Finally, to *teardown* the deployment, run:
```bash
terraform destroy
```

If you have any questions about the above instructions or issues with the
deployment reach out to Product DevOps for assistance.
