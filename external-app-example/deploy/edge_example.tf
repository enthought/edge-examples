terraform {
  backend "local" {}
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.12"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

locals {
  namespace = "edge-dev"
}

resource "kubernetes_deployment_v1" "edge-example-app" {
  metadata {
    name      = "edge-example-app"
    namespace = local.namespace
    labels = {
      app = "edge-example-app"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "edge-example-app"
      }
    }
    template {
      metadata {
        labels = {
          app = "edge-example-app"
        }
      }
      spec {
        image_pull_secrets {
          name = kubernetes_secret_v1.quay_login.metadata[0].name
        }

        volume {
          name = "secrets"

          secret {
            secret_name = kubernetes_secret_v1.edge-example-app.metadata[0].name
          }
        }

        container {
          name  = "edge-example-app"
          image = "quay.io/enthought/edge-external-app-demo:latest"
          image_pull_policy = "Always"

          env {
            name  = "SESSION_SECRET_KEY_FILE"
            value = "/secrets/secret_key"
          }
          env {
            name  = "OAUTH_CLIENT_SECRET_FILE"
            value = "/secrets/client_secret"
          }
          env {
            name  = "OAUTH_CLIENT_ID"
            value = "service-edge-app-demo-edge-external-app-demo"
          }
          env {
            name  = "OAUTH_REDIRECT_URI"
            value = "http://edge-external-app-demo.platform-devops.enthought.com/authorize"
          }
          env {
            name  = "EDGE_BASE_URL"
            value = "https://edge.enthought.com"
          }

          volume_mount {
            name       = "secrets"
            mount_path = "/secrets"
            read_only  = true
          }

          resources {
            requests = {
              cpu = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu = "100m"
              memory = "256Mi"
            }
          }
          port {
            container_port = 8020
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "edge-example-app" {
  metadata {
    name      = "edge-example-app"
    namespace = local.namespace
  }

  spec {
    selector = {
      app = "edge-example-app"
    }
    port {
      port        = 8020
      target_port = "8020"
    }
  }
}

resource "random_password" "edge-example-app" {
  length  = 24
  special = false
}

variable "client_secret" {
  type = string
}

resource "kubernetes_secret_v1" "edge-example-app" {
  metadata {
    name      = "edge-example-app"
    namespace = local.namespace
  }

  data = {
    secret_key        = random_password.edge-example-app.result
    client_secret     = var.client_secret
  }
}

resource "kubernetes_manifest" "virtualservice_edge-example-app" {
  manifest = {
    apiVersion = "networking.istio.io/v1alpha3"
    kind = "VirtualService"
    metadata = {
      name = "edge-example-app"
      namespace = local.namespace
    }
    spec = {
      gateways = [
        "istio-ingress/platform-devops-enthought-com"
      ]
      hosts = [
        "edge-external-app-demo.platform-devops.enthought.com"
      ]
      http = [
        {
          match = [
            {
              uri = {
                prefix = "/"
              }
            }
          ]
          route = [
            {
              destination = {
                host = kubernetes_service_v1.edge-example-app.metadata[0].name
                port = {
                  number = 8020
                }
              }
            }
          ]
        }
      ]
    }
  }
}
