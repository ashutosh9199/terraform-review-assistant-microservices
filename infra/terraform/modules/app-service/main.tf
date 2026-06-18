resource "azurerm_service_plan" "this" {
  name                = "${var.name_prefix}-asp"
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags                = var.tags
}

resource "azurerm_linux_web_app" "api" {
  name                = "${var.name_prefix}-api"
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.this.id
  https_only          = true
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true

    application_stack {
      docker_image_name   = var.container_image
      docker_registry_url = "https://index.docker.io"
    }
  }

  app_settings = merge(
    var.app_settings,
    {
      APPLICATIONINSIGHTS_CONNECTION_STRING = var.application_insights_connection
      ENVIRONMENT                           = "azure"
    }
  )
}
