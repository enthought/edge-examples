variable "prefix" {
  type = string
}

variable "app_name" {
  type = string
}

variable "component_name" {
  type = string
}

variable "service_port" {
  type = number
}

variable "container_port" {
  type = number
}

variable "namespace" {
  type = string
}

variable "inject_headers" {
  type = map(string)
  default = {}
}

variable "istio_ingress_namespace" {
  type        = string
  default     = "istio-ingress"
}

variable "istio_gateway_name" {
  type        = string
  default     = "local-enthought-com"
}