# Virtual Network with a public and a private subnet.
# AKS nodes live in the private subnet; the public subnet is reserved for
# public-facing infrastructure (e.g. an ingress / load balancer frontend).

resource "azurerm_virtual_network" "this" {
  name                = "${var.name_prefix}-vnet"
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = var.address_space
  tags                = var.tags
}

resource "azurerm_subnet" "public" {
  name                 = "${var.name_prefix}-snet-public"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = var.public_subnet_prefixes
}

resource "azurerm_subnet" "private" {
  name                 = "${var.name_prefix}-snet-private"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = var.private_subnet_prefixes
}
