variable "name_prefix" {
  type        = string
  description = "Application Insights naming prefix."
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name."
}

variable "location" {
  type        = string
  description = "Azure region."
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Log Analytics workspace ID."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
