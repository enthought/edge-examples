resource "kubernetes_manifest" "gateway_localhost" {
  manifest = {
    apiVersion = "networking.istio.io/v1beta1"
    kind       = "Gateway"
    metadata = {
      name      = "localhost"
      namespace = "istio-system"
    }

    spec = {
      selector = {
        istio = "ingressgateway"
      }
      servers = [
        {
          hosts = [
            "*"
          ]
          port = {
            name     = "http"
            number   = 80
            protocol = "HTTP"
          }
        },
      ]
    }
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
                  "cluster.local/ns/istio-system/sa/istio-ingressgateway-service-account"
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
        "${kubernetes_manifest.gateway_localhost.manifest.metadata.namespace}/${kubernetes_manifest.gateway_localhost.manifest.metadata.name}"
      ]
      hosts = [
        "*"
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
