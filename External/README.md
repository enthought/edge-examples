# Externally hosted app example

This example shows how to develop and deploy an externally hosted application that integrates
with Edge's upstream identity provider (Identity/Keycloak) for authentication and retrieval of user metadata.


## Before you begin

Before starting, ensure you have the following installed:

* [EDM](https://www.enthought.com/edm/), the Enthought Deployment Manager
* [Docker Desktop](https://docker.com)
* [DevSpace](https://www.devspace.sh/docs/getting-started/installation)
* [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

For this example, your ``edm.yaml`` file should have the public ``enthought/free`` and ``enthought/lgpl``
repositories enabled.

The example can be deployed and run locally or on a remote Kubernetes cluster.

### Remote deployment

For the remote deployment, please contact DevOps, who will set up a namespace, networking, Keycloak configuration 
and authentication middleware in an appropriate Kubernetes cluster for your use case.

The team will also guide you through the process of adjusting the configuration of this example to work with the
remote deployment.

### Local deployment

The local deployment options relies on a local Kubernetes cluster, such as Docker Desktop's built-in option.
You can enable the Kubernetes feature in Docker Desktop under Settings -> Kubernetes -> Enable Kubernetes.

User metadata is passed to the application via HTTP headers. For the local deployment, we are mocking the headers
by injecting test user metadata into incoming requests via Istio.

After enabling Kubernetes in Docker Desktop, you will need to install Istio.
[Installing Istio's default profile](https://istio.io/latest/docs/setup/install/istioctl/) is sufficient for this example. 

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
