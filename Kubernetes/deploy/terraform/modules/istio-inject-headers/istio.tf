# This data source is only here to provoke an _obvious_ error if the
# chosen istio gateway does not exist.
data "kubernetes_resource" "gateway" {
  api_version = "networking.istio.io/v1"
  kind        = "Gateway"
  metadata {
    name      = var.istio_gateway_name
    namespace = var.istio_ingress_namespace
  }
}

resource "kubernetes_manifest" "telemetry_deployment" {
  manifest = {
    apiVersion = "telemetry.istio.io/v1alpha1"
    kind       = "Telemetry"
    metadata = {
      name      = "deployment"
      namespace = data.kubernetes_namespace_v1.this.metadata.0.name
    }
    spec = {
      accessLogging = [
        {
          providers = [
            {
              name = "envoy"
            }
          ]
          filter = {
            expression = "response.code >= 400"
          }
        }
      ]
    }
  }
}

resource "kubernetes_manifest" "authorization_policy_allow_nothing" {
  manifest = {
    apiVersion = "security.istio.io/v1beta1"
    kind       = "AuthorizationPolicy"
    metadata = {
      name      = "allow-nothing"
      namespace = data.kubernetes_namespace_v1.this.metadata.0.name
    }
    spec = {}
  }
}

resource "kubernetes_manifest" "authorization_policy_backend" {
  manifest = {
    apiVersion = "security.istio.io/v1beta1"
    kind       = "AuthorizationPolicy"
    metadata = {
      name      = "${var.app_name}-${var.component_name}"
      namespace = data.kubernetes_namespace_v1.this.metadata.0.name
    }
    spec = {
      selector = {
        matchLabels = {
          "app.kubernetes.io/name"      = var.app_name
          "app.kubernetes.io/component" = var.component_name
        }
      }
      action = "ALLOW"
      rules = [
        {
          from = [
            {
              source = {
                principals = [
                  var.istio_ingress_sa_principal
                ]
              }
            }
          ]
          to = [
            {
              operation = {
                ports = [
                  var.container_port
                ]
              }
            }
          ]
        }
      ]
    }
  }
  field_manager {
    force_conflicts = true
  }
}


resource "kubernetes_manifest" "virtualservice" {
  manifest = {
    apiVersion = "networking.istio.io/v1beta1"
    kind       = "VirtualService"
    metadata = {
      name      = var.app_name
      namespace = data.kubernetes_namespace_v1.this.metadata.0.name
    }
    spec = {
      gateways = [
        "${var.istio_ingress_namespace}/${var.istio_gateway_name}",
      ]
      hosts = [
        "${var.app_name}.local.enthought.com",
      ]
      http = [
        {
          match = [
            {
              uri = {
                prefix = trimsuffix(var.prefix, "/")
              }
            }
          ]
          headers = {
            request = {
              set = merge(
                {
                  "X-Forwarded-For" = "%DOWNSTREAM_REMOTE_ADDRESS_WITHOUT_PORT%"
                },
                {
                  
                },
                { for k, v in var.inject_headers : k => v }
              )
            }
          }
          route = [
            {
              destination = {
                host = "${var.app_name}-${var.component_name}.${data.kubernetes_namespace_v1.this.metadata.0.name}.svc.cluster.local"
                port = {
                  number = var.service_port
                }
              }
            }
          ]
        }
      ]
    }
  }
}
