resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_mssql_server" "this" {
  name                          = substr("${var.name_prefix}-sql-${random_string.suffix.result}", 0, 63)
  resource_group_name           = var.resource_group_name
  location                      = var.location
  version                       = "12.0"
  administrator_login           = var.admin_login
  administrator_login_password  = var.admin_password
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true
  tags                          = var.tags
}

resource "azurerm_mssql_database" "this" {
  name           = "terraform-review"
  server_id      = azurerm_mssql_server.this.id
  sku_name       = "S0"
  zone_redundant = false
  tags           = var.tags
}
