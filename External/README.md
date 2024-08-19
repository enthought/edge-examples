# Kubernetes hosted app example

This example demonstrates how to develop and deploy a Kubernetes hosted application alongside Enthought Edge.

It is designed to integrate with the authentication, monitoring, logging and scaling tooling available
on Enthought-managed Kubernetes clusters, while retrieving user metadata from the upstream identity provider
(Identity/Keycloak) shared with Edge.

## Before you begin

Before starting, ensure you have the following installed:

* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager
* A local Docker installation for building container images and hosting a Kubernetes cluster (for local deployment):
  * [Docker Desktop](https://docs.docker.com/desktop/) or 
  * [Minikube](https://minikube.sigs.k8s.io/docs/start/)
* [DevSpace](https://www.devspace.sh/docs/getting-started/installation)
* [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

For this example, your ``edm.yaml`` file should have the public ``enthought/free`` and ``enthought/lgpl``
repositories enabled.

The example can be deployed and run locally or on a remote Kubernetes cluster.

### Local deployment

The local deployment option relies on a local Kubernetes cluster and has been tested with Docker Desktop's built-in Kubernetes feature and with Minikube.

User metadata is passed to the application via HTTP headers. For the local deployment, we are mocking the headers
by injecting test user metadata into incoming requests via Istio.

#### Docker Desktop

For Docker Desktop, you will need to perform the following steps:

1. Make sure that Docker Desktop has been installed and is running.
2. Enable the built-in Kubernetes feature via Settings -> Kubernetes -> Enable Kubernetes.
3. Install Istio. [Istio's default profile](https://istio.io/latest/docs/setup/install/istioctl/#install-istio-using-the-default-profile) is sufficient for this example.

#### Minikube

1. Make sure that the Minikube CLI has been installed.
2. Start a Minikube cluster (with Istio) by running `minikube start --addons="istio-provisioner,istio"`

> [!NOTE]
> Minikube will automatically try to detect the appropriate driver for your system. If you want to use a specific driver, you can specify it with the `--driver` flag. See the [Minikube documentation](https://minikube.sigs.k8s.io/docs/start/) for more information. We have successfully tested this example with the `docker` driver, `hyper-v` driver on Windows and `hyperkit` driver on MacOS.

### Remote deployment

For the remote deployment, please contact DevOps, who will set up a namespace, networking, Keycloak configuration 
and authentication middleware in an appropriate Kubernetes cluster for your use case.

The team will also guide you through the process of adjusting the configuration of this example to work with the
remote deployment.

Remote deployments will use the actual user metadata provided by Identity/Keycloak and therefore share a login session with Edge.

## Quick start

The following steps will guide you through the process of deploying the example app locally.

1. Make sure that your Kubenetes context is pointing to the local cluster by running ``devspace use context docker-desktop``.

2. Run ``devspace run terraform-init`` to initialize the Terraform workspace that will deploy the application resources into your local Kubernetes cluster.

3. **Optionally**, run ``devspace run create-edm-devenv`` to create a development environment in EDM. This will create a new EDM environment called ``edge-externally-hosted-app`` and install the required dependencies. Note that is only meant to provide a development environment for your IDE and is not required for the application to run.

4. Run ``devspace dev`` to start the application in development mode. This will build the Docker image, deploy the application and set up a port-forward to access it.  
You should now be able to access the application at [http://localhost:8080/external/app/example](http://localhost:8080/external/app/example).

You can now start developing your application. The application is set up to sync changes to the source code and automatically reload. Application logs are streamed to the terminal.

To stop the sync and the application, press `Ctrl+C` in the terminal where `devspace dev` is running.

## Cleaning up

To clean up the resources created by the example, run ``devspace purge``.
