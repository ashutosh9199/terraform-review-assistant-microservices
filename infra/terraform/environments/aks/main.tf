# AKS environment: VNet + AKS + ACR + managed services + Workload Identity.
# Every resource is tagged via var.tags (Environment + Owner). No secrets live
# here — the pod reaches Blob storage through Workload Identity, and CI
# authenticates with federated OIDC.

module "resource_group" {
  source   = "../../modules/resource-group"
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = var.tags
}

module "network" {
  source              = "../../modules/network"
  name_prefix         = var.name_prefix
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

# Managed cloud service reached from pods via Workload Identity (capstone §A/§D).
module "storage" {
  source              = "../../modules/storage-account"
  name_prefix         = replace(var.name_prefix, "-", "")
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

module "key_vault" {
  source              = "../../modules/key-vault"
  name_prefix         = replace(var.name_prefix, "-", "")
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

module "aks" {
  source                     = "../../modules/aks"
  name_prefix                = var.name_prefix
  resource_group_name        = module.resource_group.name
  location                   = module.resource_group.location
  kubernetes_version         = var.kubernetes_version
  system_node_vm_size        = var.system_node_vm_size
  user_node_vm_size          = var.user_node_vm_size
  subnet_id                  = module.network.private_subnet_id
  vnet_id                    = module.network.vnet_id
  log_analytics_workspace_id = module.monitoring.workspace_id
  tags                       = var.tags
}

module "acr" {
  source                     = "../../modules/acr"
  name_prefix                = var.name_prefix
  resource_group_name        = module.resource_group.name
  location                   = module.resource_group.location
  kubelet_identity_object_id = module.aks.kubelet_identity_object_id
  tags                       = var.tags
}

module "workload_identity" {
  source               = "../../modules/workload-identity"
  name_prefix          = var.name_prefix
  resource_group_name  = module.resource_group.name
  location             = module.resource_group.location
  oidc_issuer_url      = module.aks.oidc_issuer_url
  namespace            = var.k8s_namespace
  service_account_name = var.k8s_service_account
  storage_account_id   = module.storage.account_id
  tags                 = var.tags
}
