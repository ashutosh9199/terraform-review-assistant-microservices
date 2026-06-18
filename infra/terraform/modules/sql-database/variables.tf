variable "name_prefix" {
  type        = string
  description = "SQL naming prefix."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "admin_login" {
  type        = string
  description = "SQL admin login."
}

variable "admin_password" {
  type        = string
  description = "SQL admin password."
  sensitive   = true
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
