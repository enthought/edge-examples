# resource "data.kubernetes_namespace_v1" "this" {
#   metadata {
#     name = var.namespace
#     labels = {
#       istio-injection = "enabled"
#     }
#   }
# }

data "kubernetes_namespace_v1" "this" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_labels" "this" {
  api_version = "v1"
  kind       = "Namespace"

  metadata {
    name      = data.kubernetes_namespace_v1.this.metadata.0.name
  }

  labels = {
    istio-injection = "enabled"
  }
}
