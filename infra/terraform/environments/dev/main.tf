module "resource_group" {
  source   = "../../modules/resource-group"
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = var.tags
}

module "storage" {
  source              = "../../modules/storage-account"
  name_prefix         = replace(var.name_prefix, "-", "")
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

module "monitoring" {
  source              = "../../modules/monitoring"
  name_prefix         = var.name_prefix
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

module "app_insights" {
  source                     = "../../modules/application-insights"
  name_prefix                = var.name_prefix
  resource_group_name        = module.resource_group.name
  location                   = module.resource_group.location
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = var.tags
}

module "key_vault" {
  source              = "../../modules/key-vault"
  name_prefix         = replace(var.name_prefix, "-", "")
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

module "sql" {
  source              = "../../modules/sql-database"
  name_prefix         = replace(var.name_prefix, "-", "")
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  admin_login         = var.sql_admin_login
  admin_password      = var.sql_admin_password
  tags                = var.tags
}

module "api_app" {
  source                          = "../../modules/app-service"
  name_prefix                     = var.name_prefix
  resource_group_name             = module.resource_group.name
  location                        = module.resource_group.location
  container_image                 = var.container_image
  application_insights_connection = module.app_insights.connection_string
  app_settings = {
    DATABASE_URL        = "mssql+pyodbc://${var.sql_admin_login}:${var.sql_admin_password}@${module.sql.server_fqdn}:1433/${module.sql.database_name}"
    STORAGE_BACKEND     = "azure"
    KEY_VAULT_URL       = module.key_vault.vault_uri
    AZURE_STORAGE_NAME  = module.storage.account_name
    AZURE_STORAGE_CONTAINER = module.storage.container_name
  }
  tags = var.tags
}
