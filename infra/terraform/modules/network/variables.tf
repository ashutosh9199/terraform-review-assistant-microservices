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

variable "address_space" {
  type        = list(string)
  description = "VNet address space."
  default     = ["10.0.0.0/16"]
}

variable "public_subnet_prefixes" {
  type        = list(string)
  description = "Address prefixes for the public subnet."
  default     = ["10.0.1.0/24"]
}

variable "private_subnet_prefixes" {
  type        = list(string)
  description = "Address prefixes for the private subnet (AKS nodes)."
  default     = ["10.0.16.0/20"]
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
