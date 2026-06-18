variable "name_prefix" {
  type        = string
  description = "App Service naming prefix."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "container_image" {
  type        = string
  description = "Container image."
}

variable "application_insights_connection" {
  type        = string
  description = "Application Insights connection string."
  sensitive   = true
}

variable "app_settings" {
  type        = map(string)
  description = "Application settings."
  default     = {}
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
