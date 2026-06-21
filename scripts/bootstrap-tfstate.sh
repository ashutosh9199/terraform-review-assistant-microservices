#!/usr/bin/env bash
#
# Creates the Azure Storage Account that holds Terraform remote state.
# Run ONCE (with `az login` done) before the first `terraform init` in
# infra/terraform/environments/aks. Azure blob storage gives native state
# locking via blob leases (capstone §A: "remote state with locking").
#
# Usage:  ./scripts/bootstrap-tfstate.sh
# Env overrides: LOCATION, TFSTATE_RG, TFSTATE_SA, TFSTATE_CONTAINER

set -euo pipefail

LOCATION="${LOCATION:-eastus}"
RG="${TFSTATE_RG:-tra-tfstate-rg}"
SA="${TFSTATE_SA:-tratfstate$(printf '%05d%05d' "$((RANDOM))" "$((RANDOM))")}"
CONTAINER="${TFSTATE_CONTAINER:-tfstate}"
SA="$(echo "${SA:0:24}" | tr '[:upper:]' '[:lower:]')"

echo "Creating resource group '$RG' in $LOCATION ..."
az group create --name "$RG" --location "$LOCATION" --output none

echo "Creating storage account '$SA' ..."
az storage account create \
  --name "$SA" --resource-group "$RG" --location "$LOCATION" \
  --sku Standard_LRS --encryption-services blob \
  --min-tls-version TLS1_2 --allow-blob-public-access false \
  --output none

echo "Creating container '$CONTAINER' ..."
az storage container create \
  --name "$CONTAINER" --account-name "$SA" --auth-mode login \
  --output none

cat <<EOF

State backend ready. Create infra/terraform/environments/aks/backend.hcl with:

  resource_group_name  = "$RG"
  storage_account_name = "$SA"
  container_name       = "$CONTAINER"
  key                  = "aks/terraform.tfstate"
  use_azuread_auth     = true

Then:  cd infra/terraform/environments/aks && terraform init -backend-config=backend.hcl
EOF
