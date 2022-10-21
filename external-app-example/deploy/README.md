
# Deploying the Edge External App Demo

You can deploy this application if you have been granted access to the `edge-dev`
namespace by Product DevOps

## Requirements

The requirements are:
- Access to the `edge-dev` namespace from Product DevOps
- A kube config file from Product DevOps, installed at `~/.kube/config`
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
- [`kubelogin`](https://github.com/int128/kubelogin)
- [`terraform`](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- A client ID from Edge (see above)
- A `quay.io` username and password with access to the `quay.io/enthough/edge-external-app-demo` repo

## Deploying Using Terraform

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

## Deployment Configuration

If you are deploying a fork of this application to a different domain name,
you must *first* register the application on Edge using your desired `redirect_uri`
with the new domain name. Contact Product DevOps to get a new domain hosted 
on `platform-devops.enthought.com`.

After you have completed the OAuth client registration process,
you must configure several values within the Terraform deployment files:
- Optionally, change the [`namespace`](./edge_example.tf#L16) and app name from the default `edge-example-app` to a different namespace provided by Product DevOps
- [`container image`](./edge_example.tf#L56) should be your application's published container
- [`OAUTH_CLIENT_ID`](./edge_example.tf#L69) from the application registration process
- [`OAUTH_REDIRECT_URI`](./edge_example.tf#L73) should be the `/authorize` endpoint wherever your app will be deployed
- [VirtualService `host`](./edge_example.tf#L156) should be your new deployed domain name