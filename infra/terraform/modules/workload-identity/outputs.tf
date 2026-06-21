output "client_id" {
  description = "Managed identity client ID — annotate the K8s ServiceAccount with this."
  value       = azurerm_user_assigned_identity.this.client_id
}

output "principal_id" {
  value = azurerm_user_assigned_identity.this.principal_id
}

output "identity_name" {
  value = azurerm_user_assigned_identity.this.name
}
