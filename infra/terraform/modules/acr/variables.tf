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

variable "kubelet_identity_object_id" {
  type        = string
  description = "AKS kubelet identity object ID granted AcrPull."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
