# Externally-Hosted App Example

This folder contains a Flask + React application that showcases how to
integrate an external web app with Edge, by using JupyterHub as the OAuth2 provider.

## Pre-Requisites

To integrate your external web app with Edge, you need to know the hostname of where
your app will be hosted. For this demonstration, we will integrate the application deployed
to [`https://edge-external-app-demo.platform-devops.enthought.com`](https://edge-external-app-demo.platform-devops.enthought.com)


## Application Requirements

Edge handles OAuth for your external web application. The requirements for authentication
in this example Flask application are handled in [`api/auth.py`](./api/auth.py). These include:
- An [`authenticated` decorator](./src/api/auth.py#L25)
- A [`/login` endpoint with OAuth redirect to Edge](./src/api/auth.py#L41)
- A [`/authorize` endpoint to Edge OAuth responses](./src/api/auth.#L57)

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

The result will look similar to this:

```python
{'client_id': 'service-edge-app-default-edge-external-app-demo',
 'client_secret': 'RANDOM_CLIENT_SECRET',
 'redirect_uri': 'https://edge-external-app-demo.platform-devops.enthought.com/authorize'}
 ```

These values (along with Edge's base URL `https://edge-dev-main.platform-devops.enthought.com`)
should be provided to your application when you deploy it. This example application
provides this configuration to [`authlib`](./src/app.py#L31)

## Accessing The Application

Your application should now appear in Edge's home screen as a tile named
"Edge External App Demo, v1.0.0". Clicking on the tile will take you to your application.
If you click the Login button on the example application, it will perform a login
using Edge.

 ## Running the Application Locally

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

To build the application, use:

```commandline
python -m ci build
```

You can run this application in debug mode without Edge authentication integration using:

```commandline
python -m ci watch backend
```

## Deploying the Application

You can deploy this application if you have access to the `edge-dev`
namespace from Product DevOps

### Requirements

The requirements are:
- Access to the `edge-dev` namespace from Product DevOps
- A kube config file from Product DevOps, installed at `~/.kube/config`
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
- [`kubelogin`](https://github.com/int128/kubelogin)
- [`terraform`](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- A client ID from Edge (see above)
- A `quay.io` username and password with access to the `quay.io/enthough/edge-external-app-demo` repo

If it's your first time deploying the application, make sure you follow the
steps below as they describe how to install and configure `kubectl` and
the `terraform` CLI:

### Deploying Using Terraform

1. Switch your namespace to `edge-dev`
```bash
kubectl config set-context --current --namespace=edge-dev
```
2. Test your configuration by viewing existing pods. You will be prompted for a login.
```bash
kubectl get pods
```
3. `cd` to the `deploy` directory.

4. If it's your first time deploying the demo application from your environment,
run:
```bash
terraform init
```
5. To *deploy* the demo application, run:
```bash
terraform apply
```

You will be prompted for the client ID, `quay.io` password and `quay.io` username.

To check that your deployment succeded you can run `kubectl describe pod` or 
`kubectl describe deploy`.

You can open the demo app in your browser by going to
[`https://edge-external-app-demo.platform-devops.enthought.com`](https://edge-external-app-demo.platform-devops.enthought.com)
