# AKS Deployment Runbook (Track B)

End-to-end steps to provision the infrastructure, wire CI/CD, and deploy the app.
Run from a machine with `az`, `terraform` (>=1.6), and `kubectl`, logged in via `az login`.

## 1. Remote Terraform state (once)
```bash
./scripts/bootstrap-tfstate.sh        # creates the state storage account + container
# copy the printed values into:
cp infra/terraform/environments/aks/backend.hcl.example \
   infra/terraform/environments/aks/backend.hcl
# edit backend.hcl with the printed storage account name
```

## 2. Provision infrastructure
```bash
cd infra/terraform/environments/aks
terraform init -backend-config=backend.hcl
terraform apply        # review the plan, then approve
terraform output       # note the values below
```
Key outputs: `acr_login_server`, `aks_cluster_name`, `resource_group_name`,
`storage_account_name`, `workload_identity_client_id`.

> CI alternative: push to `main` and let `terraform-apply.yml` run plan → approval → apply.

## 3. GitHub OIDC + secrets/variables (once)
```bash
GH_ORG=<your-gh-username-or-org> ./scripts/setup-github-oidc.sh
```
Then in GitHub → Settings → Secrets and variables → Actions add:

**Secrets:** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
`JWT_SECRET_KEY` (a strong random string).

**Variables:** `ACR_LOGIN_SERVER`, `AKS_CLUSTER`, `AKS_RG`, `AZURE_STORAGE_ACCOUNT`,
`WORKLOAD_IDENTITY_CLIENT_ID`, `TFSTATE_RG`, `TFSTATE_SA`, `TFSTATE_CONTAINER`
(values come from `terraform output` and the bootstrap script).

Create two GitHub **Environments** with required reviewers (the approval gates):
`production` (used by `deploy.yml`) and `infrastructure` (used by `terraform-apply.yml`).

## 4. Build, scan, push, deploy
Push to `main`:
- `build.yml` → lint/test, build 8 multistage images, Trivy gate, push to ACR.
- `deploy.yml` → waits for your approval, then deploys to AKS and smoke-tests.

## 5. Verify (rubric checks)
```bash
az aks get-credentials -g "$AKS_RG" -n "$AKS_CLUSTER"
kubectl get pods -n production                 # all Running
kubectl get svc frontend -n production         # EXTERNAL-IP assigned
curl http://<EXTERNAL-IP>/healthz              # 200 OK

# Workload Identity: pod reaches Blob with NO static creds
kubectl logs deploy/upload-service -n production
kubectl exec deploy/upload-service -n production -- env | grep -i azure
#   -> only AZURE_STORAGE_ACCOUNT/CONTAINER + the injected federated-token vars,
#      no account key or connection string.
```

## Secret-history audit (before sharing the repo)
```bash
# No state files, env files, or real secrets tracked:
git ls-files | grep -E '\.tfstate|\.env$|secret\.yaml$|kubeconfig' && echo "FOUND" || echo "clean"
# Scan history for obvious secrets (optional, if gitleaks installed):
gitleaks detect --no-banner || true
```
