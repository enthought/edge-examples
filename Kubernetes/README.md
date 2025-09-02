# Kubernetes hosted app example

This example demonstrates how to develop and deploy a Kubernetes hosted application alongside Enthought Edge.

It is designed to integrate with the authentication, monitoring, logging and scaling tooling available
on Enthought-managed Kubernetes clusters, while retrieving user metadata from the upstream identity provider
(Identity/Keycloak) shared with Edge.

## Before you begin

Before starting, ensure you have the following installed:

* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager
* [Docker Desktop](https://docs.docker.com/desktop/) for building container images and hosting a Kubernetes cluster (for local deployment) 
* [DevSpace](https://www.devspace.sh/docs/getting-started/installation)
* [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

For this example, your `edm.yaml` file should have the public `enthought/free` and `enthought/lgpl`
repositories enabled.

The example can be deployed and run locally or on a remote Kubernetes cluster.

### Local deployment

The local deployment option relies on a local Kubernetes cluster and has been tested with Docker Desktop's built-in Kubernetes feature,
using the `kind` (Kubernetes in Docker) cluster option.

User metadata is passed to the application via HTTP headers. For the local deployment, we are mocking the headers
by injecting test user metadata into incoming requests via Istio.

We recommend using Docker Desktop with `kind` for local development, since it simplifies the setup of Istio and lacks the licensing restrictions of Docker Desktop.

#### Docker Desktop

For Docker Desktop, you will need to perform the following steps:

1. Make sure that Docker Desktop has been installed and is running.
2. Enable the built-in Kubernetes feature via Settings -> Kubernetes -> Enable Kubernetes. Make sure the Cluster settings are set to use the `kind` cluster provisioning method
3. Install Istio. [Istio's default profile](https://istio.io/latest/docs/setup/install/istioctl/#install-istio-using-the-default-profile) is sufficient for this example.
4. Download or clone the [`terraform-kubernetes-local-bootstrap`](https://github.com/enthought/terraform-kubernetes-local-bootstrap) repository
and follow the [`README.md`](https://github.com/enthought/terraform-kubernetes-local-bootstrap/blob/main/README.md) instructions. This will install CoreDNS and make your
application be available locally at `https://example.local.enthought.com`.

### Remote deployment

For the remote deployment, please contact the DevOps team, who will set up a namespace, networking, 
Keycloak configuration and authentication middleware in an appropriate Kubernetes cluster for your use case.

The team will also guide you through the process of adjusting the configuration of this example to work with the
remote deployment.

Remote deployments will use the actual user metadata provided by Identity/Keycloak and therefore share a login session with Edge.

## Quick start

The following steps will guide you through the process of deploying the example app locally.

1. Make sure that your Kubenetes context is pointing to the local cluster by running `devspace use context docker-desktop`.

2. Run `devspace run terraform-init` to initialize the Terraform workspace that will deploy the application resources into your local Kubernetes cluster.

3. **Optionally**, run `devspace run create-edm-devenv` to create a development environment in EDM. This will create a new EDM environment called `edge-kubernetes-app-example` and install the required dependencies. Note that is only meant to provide a development environment for your IDE and is not required for the application to run.

4. Run `devspace dev` to start the application in development mode. This will build the Docker image, deploy the application and set up a port-forward to access it.  
You should now be able to access the application at [http://localhost:8080/k8s/default/example](http://localhost:8080/k8s/default/example).

You can now start developing your application. The application is set up to sync changes to the source code and automatically reload. Application logs are streamed to the terminal.

To stop the sync and the application, press `Ctrl+C` in the terminal where `devspace dev` is running.

## Cleaning up

To clean up the resources created by the example, run `devspace purge`.
