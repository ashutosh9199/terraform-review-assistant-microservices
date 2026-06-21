output "cluster_name" {
  value = azurerm_kubernetes_cluster.this.name
}

output "cluster_id" {
  value = azurerm_kubernetes_cluster.this.id
}

output "node_resource_group" {
  value = azurerm_kubernetes_cluster.this.node_resource_group
}

output "oidc_issuer_url" {
  description = "OIDC issuer URL used to federate Workload Identity credentials."
  value       = azurerm_kubernetes_cluster.this.oidc_issuer_url
}

output "identity_principal_id" {
  description = "Cluster system-assigned identity principal ID."
  value       = azurerm_kubernetes_cluster.this.identity[0].principal_id
}

output "kubelet_identity_object_id" {
  description = "Kubelet identity object ID (granted AcrPull on the registry)."
  value       = azurerm_kubernetes_cluster.this.kubelet_identity[0].object_id
}
