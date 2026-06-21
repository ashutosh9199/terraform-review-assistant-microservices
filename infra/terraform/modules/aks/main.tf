# AKS cluster with a system node pool and a user node pool, both autoscaling.
# OIDC issuer + Workload Identity are enabled so pods can authenticate to Azure
# services using a federated managed identity (no static credentials).

resource "azurerm_kubernetes_cluster" "this" {
  name                = "${var.name_prefix}-aks"
  resource_group_name = var.resource_group_name
  location            = var.location
  dns_prefix          = "${var.name_prefix}-aks"
  kubernetes_version  = var.kubernetes_version

  oidc_issuer_enabled               = true
  workload_identity_enabled         = true
  role_based_access_control_enabled = true

  # System node pool (autoscaling). On the 4-vCPU trial quota it is pinned to a
  # single node and also schedules application pods (no critical-addons taint).
  default_node_pool {
    name                 = "system"
    vm_size              = var.system_node_vm_size
    vnet_subnet_id       = var.subnet_id
    orchestrator_version = var.kubernetes_version
    enable_auto_scaling  = true
    min_count            = 1
    max_count            = var.system_node_max_count
    tags                 = var.tags
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = var.service_cidr
    dns_service_ip    = var.dns_service_ip
  }

  # Stream container logs/metrics into Log Analytics (Container Insights).
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  tags = var.tags
}

# User node pool (autoscaling) for application workloads.
resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.this.id
  vm_size               = var.user_node_vm_size
  vnet_subnet_id        = var.subnet_id
  orchestrator_version  = var.kubernetes_version
  mode                  = "User"
  enable_auto_scaling   = true
  min_count             = 1
  max_count             = var.user_node_max_count
  tags                  = var.tags
}

# The cluster's managed identity needs to manage resources (load balancers,
# subnet joins) inside the BYO virtual network.
resource "azurerm_role_assignment" "network_contributor" {
  scope                = var.vnet_id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_kubernetes_cluster.this.identity[0].principal_id
}
