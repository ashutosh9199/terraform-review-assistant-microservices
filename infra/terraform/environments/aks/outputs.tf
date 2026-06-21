# Outputs document cluster endpoints and the values the K8s manifests / CI need.

output "resource_group_name" {
  value = module.resource_group.name
}

output "aks_cluster_name" {
  value = module.aks.cluster_name
}

output "aks_node_resource_group" {
  value = module.aks.node_resource_group
}

output "aks_oidc_issuer_url" {
  value = module.aks.oidc_issuer_url
}

output "acr_login_server" {
  description = "Set as the ACR_LOGIN_SERVER GitHub variable; prefix for image tags."
  value       = module.acr.login_server
}

output "workload_identity_client_id" {
  description = "Annotate the upload-service ServiceAccount with this client ID."
  value       = module.workload_identity.client_id
}

output "storage_account_name" {
  description = "Set as AZURE_STORAGE_ACCOUNT in the ConfigMap (no key needed)."
  value       = module.storage.account_name
}

output "storage_container_name" {
  value = module.storage.container_name
}

output "key_vault_uri" {
  value = module.key_vault.vault_uri
}

output "app_insights_connection_string" {
  description = "Store in the K8s Secret (sensitive)."
  value       = module.app_insights.connection_string
  sensitive   = true
}
