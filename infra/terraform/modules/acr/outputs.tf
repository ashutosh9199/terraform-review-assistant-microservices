output "login_server" {
  description = "ACR login server (e.g. traaksacrxxxxxx.azurecr.io)."
  value       = azurerm_container_registry.this.login_server
}

output "registry_name" {
  value = azurerm_container_registry.this.name
}

output "registry_id" {
  value = azurerm_container_registry.this.id
}
