variable "location" {
  type        = string
  description = "Azure region."
  default     = "eastus"
}

variable "name_prefix" {
  type        = string
  description = "Resource naming prefix."
  default     = "tra-aks"
}

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version (capstone requires v1.29+)."
  default     = "1.29"
}

variable "system_node_vm_size" {
  type        = string
  description = "VM size for the AKS system node pool."
  default     = "Standard_D2s_v5"
}

variable "user_node_vm_size" {
  type        = string
  description = "VM size for the AKS user node pool."
  default     = "Standard_D2s_v5"
}

variable "k8s_namespace" {
  type        = string
  description = "Kubernetes namespace that the federated ServiceAccount lives in."
  default     = "production"
}

variable "k8s_service_account" {
  type        = string
  description = "Kubernetes ServiceAccount federated to the Blob managed identity."
  default     = "upload-service"
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to every resource (Environment + Owner required by the rubric)."
  default = {
    Environment = "production"
    Owner       = "platform-team"
    Project     = "terraform-review-assistant"
    ManagedBy   = "terraform"
  }
}
