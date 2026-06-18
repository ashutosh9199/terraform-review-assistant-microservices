output "resource_group_name" {
  value = module.resource_group.name
}

output "storage_account_name" {
  value = module.storage.account_name
}

output "key_vault_uri" {
  value = module.key_vault.vault_uri
}

output "api_app_name" {
  value = module.api_app.app_name
}
