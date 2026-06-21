terraform {
  # Remote state in an Azure Storage Account. Azure blob storage provides
  # native state locking via blob leases (capstone §A: "remote state with locking").
  #
  # This is a PARTIAL backend config — the storage account is created first by
  # scripts/bootstrap-tfstate.sh, then values are supplied at init time:
  #
  #   terraform init -backend-config=backend.hcl
  #
  # See backend.hcl.example. CI authenticates to the backend with OIDC
  # (ARM_USE_OIDC=true); locally, `az login` + use_azuread_auth is used.
  backend "azurerm" {}
}
