provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = var.kube_context
}

locals {
  app_name       = "example"
  component_name = "backend"
  prefix         = "/external/default/example/"
  service_port   = 9000
  container_port = 9000

  inject_headers = {
    "X-Forwarded-Email"              = "testuser@example.com"
    "X-Forwarded-Groups"             = "role:edge-external-app-example:user"
    "X-Forwarded-Preferred-Username" = "testuser@example.com"
    "X-Forwarded-User"               = "abababab-abab-abab-abab-abababababab"
    "X-Forwarded-Display-Name"       = "Test User"
  }
}

module "istio_inject_headers" {
  count = var.local ? 1 : 0

  source = "../../modules/istio-inject-headers"

  app_name       = local.app_name
  component_name = local.component_name
  container_port = local.container_port
  service_port   = local.service_port

  prefix = local.prefix

  namespace = var.namespace

  inject_headers = local.inject_headers
}

module "app" {
  source = "../../modules/app"

  use_nodepool = !var.local

  app_name       = local.app_name
  component_name = local.component_name
  container_port = local.container_port
  service_port   = local.service_port

  prefix = local.prefix

  namespace = var.namespace

  image_name = var.image_name
  image_tag  = var.image_tag
}
