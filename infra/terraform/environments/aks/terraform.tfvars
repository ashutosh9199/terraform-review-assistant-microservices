# Non-secret configuration (capstone §A: "no hardcoded values; use terraform.tfvars").
# Secrets are NEVER placed here — Workload Identity and OIDC remove the need for any.

location           = "eastus"
name_prefix        = "tra-aks"
kubernetes_version = "1.29"

system_node_vm_size = "Standard_D2s_v5"
user_node_vm_size   = "Standard_D2s_v5"

k8s_namespace       = "production"
k8s_service_account = "upload-service"

tags = {
  Environment = "production"
  Owner       = "platform-team"
  Project     = "terraform-review-assistant"
  ManagedBy   = "terraform"
}
