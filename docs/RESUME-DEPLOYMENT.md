# Resume Deployment (from your personal laptop)

Snapshot of the live deployment progress so it can be continued on a machine with
working `az` / `terraform` / `kubectl` (a normal network — no corporate proxy).

## Prerequisites on the new machine
- Azure CLI, Terraform >= 1.6, kubectl, Docker (only needed if building locally; CI builds anyway)
- `az login` (you are the subscription owner)
- Clone the repo, then work from it.

## What is ALREADY done (persists in the cloud / GitHub — no need to redo)
- **GitHub OIDC app** + 4 federated credentials (main, pull_request, env:production, env:infrastructure)
- **Role assignments** to the CI app: Contributor + User Access Administrator (subscription),
  Storage Blob Data Contributor (on the tfstate storage account)
- **Terraform remote state** storage: resource group `tra-tfstate-rg`, account `tratfstate2079021219`, container `tfstate`
- **GitHub secrets**: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `JWT_SECRET_KEY`
- **GitHub variables**: `TFSTATE_RG`, `TFSTATE_SA`, `TFSTATE_CONTAINER`
- **GitHub environments**: `production`, `infrastructure` (each with you as required reviewer = approval gate)
- **Partial infra created** by the first apply: resource group `tra-aks-rg`, VNet, ACR, storage,
  managed identity, Key Vault, App Insights, Log Analytics. **AKS itself failed** on a retired
  K8s version — now fixed (pinned to `1.34.8`).

## What is LEFT
1. **Re-run `terraform-apply`** (the version fix is committed) and approve the `infrastructure` gate.
   Either push a trivial change to `infra/terraform/**`, or in GitHub: Actions -> terraform-apply -> Run workflow.
   This finishes AKS + the user node pool + ACR pull role + Workload Identity federation + Blob role.
2. **Set the remaining GitHub variables** from Terraform outputs (Actions -> them, or `terraform output`):
   - `ACR_LOGIN_SERVER`  = `terraform output -raw acr_login_server`
   - `AKS_CLUSTER`       = `terraform output -raw aks_cluster_name`
   - `AKS_RG`            = `terraform output -raw resource_group_name`
   - `AZURE_STORAGE_ACCOUNT`       = `terraform output -raw storage_account_name`
   - `WORKLOAD_IDENTITY_CLIENT_ID` = `terraform output -raw workload_identity_client_id`
3. **Run `build`** (push to main or Run workflow) -> builds, Trivy-scans, pushes 8 images to ACR.
4. **Run `deploy`** -> approve the `production` gate -> applies manifests to AKS.
5. **Verify** (see docs/aks-deployment.md §5): `kubectl get pods -n production`, frontend EXTERNAL-IP,
   `curl http://<EXTERNAL-IP>/healthz`, and the upload-service Blob write via Workload Identity.

## Notes
- On the new machine there is no proxy, so you can run `terraform apply` and `kubectl` **directly**
  if you prefer, instead of via the pipelines (but the rubric wants the pipelines to have green runs).
- The specific Azure IDs (client/tenant/subscription) are in the GitHub secrets already; you can also
  re-read them with `az account show` and `az ad app list --display-name tra-github-oidc`.
- Region is `eastus`; subscription vCPU quota is 4, so node pools are `Standard_B2s` x2 (already configured).
- Tear-down when done: `az group delete -n tra-aks-rg --yes --no-wait` (and `tra-tfstate-rg` to remove state).
