variable "quay_username" {
  type = string
}

variable "quay_password" {
  type = string
}

resource "kubernetes_secret_v1" "quay_login" {
  metadata {
    name      = "quay-login"
    namespace = "edge-dev"
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "https://quay.io" = {
          auth = base64encode("${var.quay_username}:${var.quay_password}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}