# Azure Container Registry for application images.
# admin_enabled = false: no static registry username/password exists (capstone
# §7). AKS pulls images using its kubelet managed identity via the AcrPull role,
# and CI pushes using federated OIDC credentials.

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_container_registry" "this" {
  name                = substr("${replace(var.name_prefix, "-", "")}acr${random_string.suffix.result}", 0, 50)
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
  admin_enabled       = false
  tags                = var.tags
}

# Allow the AKS kubelet identity to pull images (no registry credentials).
resource "azurerm_role_assignment" "aks_pull" {
  scope                            = azurerm_container_registry.this.id
  role_definition_name             = "AcrPull"
  principal_id                     = var.kubelet_identity_object_id
  skip_service_principal_aad_check = true
}
