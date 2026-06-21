variable "name_prefix" {
  type        = string
  description = "Resource naming prefix."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "oidc_issuer_url" {
  type        = string
  description = "AKS OIDC issuer URL."
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace of the federated ServiceAccount."
  default     = "production"
}

variable "service_account_name" {
  type        = string
  description = "Kubernetes ServiceAccount name to federate."
  default     = "upload-service"
}

variable "storage_account_id" {
  type        = string
  description = "Storage account resource ID to grant blob access on."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
