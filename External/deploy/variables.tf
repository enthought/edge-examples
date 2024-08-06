variable "namespace" {
  type    = string
}

variable "kube_context" {
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

variable "prefix" {
  type    = string
  default = "/external/default/example/"
}

variable "use_nodepool" {
  type    = bool
  default = true
}

variable "app_name" {
  type    = string
  default = "example"
}

variable "component_name" {
  type    = string
  default = "backend"
}

variable "service_port" {
  type    = number
  default = 9000
}

variable "container_port" {
  type    = number
  default = 9000 
}
