# Non-secret configuration (capstone §A: "no hardcoded values; use terraform.tfvars").
# Secrets are NEVER placed here — Workload Identity and OIDC remove the need for any.

location           = "eastus"
name_prefix        = "tra-aks"
kubernetes_version = "1.34.8" # 1.29 is retired in eastus; this is region-supported and satisfies "v1.29+"

# B2s (2 vCPU) x2 = 4 vCPU, fits the trial subscription's regional quota.
system_node_vm_size = "Standard_B2s"
user_node_vm_size   = "Standard_B2s"

k8s_namespace       = "production"
k8s_service_account = "upload-service"

tags = {
  Environment = "production"
  Owner       = "platform-team"
  Project     = "terraform-review-assistant"
  ManagedBy   = "terraform"
}
