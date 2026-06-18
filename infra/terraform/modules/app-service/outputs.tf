output "app_name" {
  value = azurerm_linux_web_app.api.name
}

output "default_hostname" {
  value = azurerm_linux_web_app.api.default_hostname
}
