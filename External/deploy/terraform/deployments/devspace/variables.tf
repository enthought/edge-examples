variable "kube_context" {
  type    = string
}

variable "namespace" {
  type    = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "image_name" {
  type = string
  default = "edge-external-app-example"
}

variable "local" {
  type    = bool
  default = true
}
