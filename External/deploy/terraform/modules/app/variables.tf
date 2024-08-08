variable "namespace" {
  type    = string
}

variable "image_tag" {
  type    = string
}

variable "image_name" {
  type = string
}

variable "prefix" {
  type    = string
}

variable "use_nodepool" {
  type    = bool
}

variable "app_name" {
  type    = string
}

variable "component_name" {
  type    = string
}

variable "service_port" {
  type    = number
}

variable "container_port" {
  type    = number
}
