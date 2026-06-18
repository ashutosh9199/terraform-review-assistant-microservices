variable "location" {
  type        = string
  description = "Azure region."
  default     = "eastus"
}

variable "name_prefix" {
  type        = string
  description = "Resource naming prefix."
  default     = "tra-dev"
}

variable "sql_admin_login" {
  type        = string
  description = "SQL administrator login."
  default     = "traadmin"
}

variable "sql_admin_password" {
  type        = string
  description = "SQL administrator password."
  sensitive   = true
}

variable "container_image" {
  type        = string
  description = "Backend container image."
  default     = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default = {
    Environment = "dev"
    Project     = "terraform-review-assistant"
    Owner       = "platform"
    CostCenter  = "shared"
  }
}
