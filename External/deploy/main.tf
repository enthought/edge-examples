provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = var.kube_context
}

data "kubernetes_namespace_v1" "this" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_deployment_v1" "this" {
  metadata {
    name      = "${var.app_name}-${var.component_name}"
    namespace = data.kubernetes_namespace_v1.this.metadata.0.name
    labels = {
      "app.kubernetes.io/name"      = var.app_name
      "app.kubernetes.io/component" = var.component_name
    }
  }

  lifecycle {
    ignore_changes = [
      metadata[0].annotations["devspace.sh/replicas"]
    ]
  }

  wait_for_rollout = false

  spec {
    replicas = 1
    selector {
      match_labels = {
        "app.kubernetes.io/name"      = var.app_name
        "app.kubernetes.io/component" = var.component_name
      }
    }
    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"      = var.app_name
          "app.kubernetes.io/component" = var.component_name
        }
      }
      spec {
        container {
          name              = "main"
          image             = "${var.image_name}:${var.image_tag}"
          image_pull_policy = "IfNotPresent"

          env {
            name  = "PORT"
            value = var.container_port
          }

          env {
            name  = "PREFIX"
            value = var.prefix
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "100m"
              memory = "256Mi"
            }
          }

          port {
            container_port = var.container_port
            name           = "http"
            protocol       = "TCP"
          }
        }

        dynamic "toleration" {
          for_each = var.use_nodepool ? [1] : []
          content {
            key      = "enthought.com/node-pool-purpose"
            operator = "Equal"
            value    = var.namespace
            effect   = "NoSchedule"
          }
        }

        dynamic "affinity" {
          for_each = var.use_nodepool ? [1] : []
          content {
            node_affinity {
              required_during_scheduling_ignored_during_execution {
                node_selector_term {
                  match_expressions {
                    key      = "enthought.com/node-pool-purpose"
                    operator = "In"
                    values   = [var.namespace]
                  }
                  match_expressions {
                    key      = "karpenter.sh/capacity-type"
                    operator = "In"
                    values   = ["on-demand"]
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "this" {
  metadata {
    name      = "${var.app_name}-${var.component_name}"
    namespace = data.kubernetes_namespace_v1.this.metadata.0.name
  }

  spec {
    selector = {
      "app.kubernetes.io/name"      = var.app_name
      "app.kubernetes.io/component" = var.component_name
    }
    port {
      port         = var.service_port
      target_port  = var.container_port
      protocol     = "TCP"
    }
  }
}
