# Workload Identity for pod -> Azure Blob access with NO static credentials.
#
# A user-assigned managed identity is federated to a Kubernetes ServiceAccount
# via the AKS OIDC issuer. Pods running under that ServiceAccount receive a
# projected token that Azure exchanges for the identity's access — there is no
# connection string or account key anywhere.

resource "azurerm_user_assigned_identity" "this" {
  name                = "${var.name_prefix}-wi"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags
}

# Trust the specific Kubernetes ServiceAccount (namespace + name) on this cluster.
resource "azurerm_federated_identity_credential" "this" {
  name                = "${var.name_prefix}-fic"
  resource_group_name = var.resource_group_name
  parent_id           = azurerm_user_assigned_identity.this.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = var.oidc_issuer_url
  subject             = "system:serviceaccount:${var.namespace}:${var.service_account_name}"
}

# Grant the identity data-plane access to the storage account (blob read/write).
resource "azurerm_role_assignment" "blob" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.this.principal_id
}
