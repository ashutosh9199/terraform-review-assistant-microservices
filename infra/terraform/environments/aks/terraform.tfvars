# Non-secret configuration (capstone §A: "no hardcoded values; use terraform.tfvars").
# Secrets are NEVER placed here — Workload Identity and OIDC remove the need for any.

location           = "eastus"
name_prefix        = "tra-aks"
kubernetes_version = "1.34.8" # 1.29 is retired in eastus; this is region-supported and satisfies "v1.29+"

# D2s_v7 (2 vCPU) x2 = 4 vCPU, fits the trial subscription's regional quota.
# B2s is rejected by the AKS RP in this subscription/region ("VM size not allowed"
# - a capacity allowlist restriction, not a quota issue); D2s_v7 is on that allowlist.
system_node_vm_size = "Standard_D2s_v7"
user_node_vm_size   = "Standard_D2s_v7"

k8s_namespace       = "production"
k8s_service_account = "upload-service"

tags = {
  Environment = "production"
  Owner       = "platform-team"
  Project     = "terraform-review-assistant"
  ManagedBy   = "terraform"
}
