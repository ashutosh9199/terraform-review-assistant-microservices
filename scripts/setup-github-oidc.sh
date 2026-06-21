#!/usr/bin/env bash
#
# Configures GitHub Actions -> Azure authentication via OIDC federated
# credentials (capstone §C/§7: "No credentials exposed in logs", "GitHub
# Secrets configured for cloud credentials"). NO client secret is created —
# GitHub exchanges a short-lived OIDC token for Azure access.
#
# Run once with Azure AD app-registration + role-assignment permissions.
# Usage:  GH_ORG=<owner> ./scripts/setup-github-oidc.sh

set -euo pipefail

APP_NAME="${APP_NAME:-tra-github-oidc}"
GH_ORG="${GH_ORG:?set GH_ORG, e.g. ashutosh9199}"
GH_REPO="${GH_REPO:-terraform-review-assistant-microservices}"
SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
TENANT_ID="$(az account show --query tenantId -o tsv)"

echo "Creating AAD application '$APP_NAME' ..."
APP_ID="$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)"
az ad sp create --id "$APP_ID" --output none 2>/dev/null || true

# Federate the branches / PRs / environments the workflows run under.
for SUBJECT in \
  "repo:$GH_ORG/$GH_REPO:ref:refs/heads/main" \
  "repo:$GH_ORG/$GH_REPO:ref:refs/heads/develop" \
  "repo:$GH_ORG/$GH_REPO:pull_request" \
  "repo:$GH_ORG/$GH_REPO:environment:production" \
  "repo:$GH_ORG/$GH_REPO:environment:infrastructure"; do
  NAME="fc-$(echo "$SUBJECT" | tr '/:.' '---')"
  echo "Adding federated credential: $SUBJECT"
  az ad app federated-credential create --id "$APP_ID" --parameters "{
    \"name\": \"${NAME:0:120}\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"$SUBJECT\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }" --output none
done

# Contributor to manage resources; User Access Administrator because Terraform
# creates role assignments (AcrPull, Blob Data Contributor, Network Contributor).
az role assignment create --assignee "$APP_ID" --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID" --output none
az role assignment create --assignee "$APP_ID" --role "User Access Administrator" \
  --scope "/subscriptions/$SUBSCRIPTION_ID" --output none

cat <<EOF

Done. Add these GitHub repository secrets (Settings -> Secrets and variables -> Actions):

  AZURE_CLIENT_ID        = $APP_ID
  AZURE_TENANT_ID        = $TENANT_ID
  AZURE_SUBSCRIPTION_ID  = $SUBSCRIPTION_ID

And this repository variable:
  ACR_LOGIN_SERVER       = <terraform output -raw acr_login_server>
EOF
