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

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version (capstone requires v1.29+)."
  default     = "1.29"
}

variable "system_node_vm_size" {
  type        = string
  description = "VM size for the system node pool (B2s = 2 vCPU, fits the 4-vCPU trial quota)."
  default     = "Standard_B2s"
}

variable "user_node_vm_size" {
  type        = string
  description = "VM size for the user node pool (B2s = 2 vCPU, fits the 4-vCPU trial quota)."
  default     = "Standard_B2s"
}

variable "system_node_max_count" {
  type        = number
  description = "Max system nodes for autoscaling (1 on the 4-vCPU trial quota; raise after a quota increase)."
  default     = 1
}

variable "user_node_max_count" {
  type        = number
  description = "Max user nodes for autoscaling (1 on the 4-vCPU trial quota; raise after a quota increase)."
  default     = 1
}

variable "subnet_id" {
  type        = string
  description = "Private subnet ID for the node pools."
}

variable "vnet_id" {
  type        = string
  description = "VNet ID (for the cluster identity Network Contributor assignment)."
}

variable "log_analytics_workspace_id" {
  type        = string
  description = "Log Analytics workspace ID for Container Insights."
}

variable "service_cidr" {
  type        = string
  description = "Kubernetes service CIDR (must not overlap the VNet)."
  default     = "10.1.0.0/16"
}

variable "dns_service_ip" {
  type        = string
  description = "Kubernetes DNS service IP (within service_cidr)."
  default     = "10.1.0.10"
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}
