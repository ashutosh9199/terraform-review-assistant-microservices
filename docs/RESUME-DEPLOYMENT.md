# Teardown & Redeploy Runbook

This is the authoritative, tested sequence for tearing down the live AKS
deployment to save Azure Free Trial credit, and bringing it back up before
the evaluation call. Every command here was actually run and verified during
the 2026-06-22 deployment session -- this is not a guess.

## Why this exists

The Azure subscription backing this deployment is a **Free Trial**
(`quotaId: FreeTrial_2014-09-01`, `spendingLimit: On`), not Pay-As-You-Go.
It has a hard credit cap (~₹13,000 / ~$200) in addition to the 30-day window.
AKS nodes, the frontend's LoadBalancer public IP, and Log Analytics ingestion
all bill continuously, 24/7, even with zero traffic. If the credit hits zero,
Azure disables the subscription -- everything stops with no grace period.
Tear down when not actively demoing; redeploy with ~45-60 minutes of lead
time before you need it live again.

## Current live resource names (as of the last apply)

These came from this session's `terraform output`. **Re-run `terraform output`
after any future apply** -- `acr_login_server`, `storage_account_name`, and
`workload_identity_client_id` all regenerate with new random suffixes on
every fresh `terraform apply` (they're not derived purely from `name_prefix`),
so they WILL change after a destroy+redeploy cycle. `aks_cluster_name` and
`resource_group_name` are stable (derived directly from `var.name_prefix`).

| Output | Last known value | Stable across redeploy? |
|---|---|---|
| `resource_group_name` | `tra-aks-rg` | yes |
| `aks_cluster_name` | `tra-aks-aks` | yes |
| `acr_login_server` | `traaksacrorhf1p.azurecr.io` | **no -- re-read after apply** |
| `storage_account_name` | `traaksg21ty1` | **no -- re-read after apply** |
| `workload_identity_client_id` | `950a5427-660b-4f9e-ae2a-34a02c94cbec` | **no -- re-read after apply** |

## Teardown (run when told to, not automatically)

```bash
cd infra/terraform/environments/aks
terraform init \
  -backend-config="resource_group_name=tra-tfstate-rg" \
  -backend-config="storage_account_name=tratfstate2079021219" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=aks/terraform.tfstate" \
  -backend-config="use_azuread_auth=true"
terraform destroy
```

This removes AKS (both node pools), the VNet, ACR, the Storage Account
(**including all blobs in the `terraform-projects` container -- any uploaded
review files are lost**), Key Vault, Log Analytics + Application Insights,
the workload-identity managed identity + federated credential, and the
`tra-aks-rg` resource group itself. It does **not** touch: the `tra-tfstate-rg`
state storage, GitHub secrets/variables/environments, or the GitHub OIDC app
registration -- all of that is reused as-is on redeploy.

## Redeploy (start ~45-60 min before you need it live)

1. **Azure login** (if the session expired):
   ```bash
   az login --tenant 6513a820-7377-4300-819b-c8d5c819d6b8
   az account set --subscription aae5dce6-13b3-4a2a-83ec-df765a572f30
   ```

2. **Apply Terraform** (same `init` as above, then):
   ```bash
   terraform plan -out=tfplan
   terraform apply -auto-approve tfplan
   ```
   Takes ~10-15 min (AKS cluster + node pool creation dominates).
   Note the VM size: `terraform.tfvars` is pinned to `Standard_D2s_v7` --
   `Standard_B2s` is rejected by the AKS resource provider in this
   subscription/region (a capacity-allowlist restriction, confirmed during
   this session). Don't revert that without re-checking
   `az vm list-skus --location eastus --size <sku>` first.

3. **Re-read and update the 3 GitHub variables that changed:**
   ```bash
   terraform output -raw acr_login_server
   terraform output -raw storage_account_name
   terraform output -raw workload_identity_client_id
   ```
   ```bash
   gh variable set ACR_LOGIN_SERVER -b "<value>"
   gh variable set AZURE_STORAGE_ACCOUNT -b "<value>"
   gh variable set WORKLOAD_IDENTITY_CLIENT_ID -b "<value>"
   ```
   (`AKS_CLUSTER`/`AKS_RG` don't need resetting -- they're stable.)

4. **Trigger `build`** (rebuilds + Trivy-scans + pushes all 8 images to the
   new ACR -- the old one no longer exists):
   ```bash
   gh workflow run build.yml --ref main
   ```
   Wait for it to go green (~2-3 min). Watch with:
   ```bash
   gh run list --workflow=build.yml --limit 1
   ```

5. **`deploy` auto-triggers** on build completion. It needs your approval at
   the `production` environment gate -- approve it in the GitHub Actions UI
   (link will be in the run). This also recreates `kubernetes/monitoring/`
   (Prometheus + Grafana) automatically -- no separate step needed.

6. **Verify everything is live:**
   ```bash
   az aks get-credentials -g tra-aks-rg -n tra-aks-aks --overwrite-existing
   kubectl get pods -n production      # expect 10/10 Running
   kubectl get pods -n monitoring      # expect 2/2 Running (prometheus, grafana)
   kubectl get svc frontend -n production   # note the new EXTERNAL-IP -- it WILL differ from last time
   curl http://<NEW-EXTERNAL-IP>/healthz    # expect "ok"
   ```

7. **Update the README's Live Deployment URL** -- the LoadBalancer gets a new
   public IP every time it's recreated:
   ```bash
   # edit README.md's "URL" row to the new IP, then:
   git add README.md && git commit -m "Update live deployment IP after redeploy" && git push
   ```

8. **Grafana password is unchanged** (it's a GitHub Secret, survives
   teardown) -- still retrievable via:
   ```bash
   kubectl get secret grafana-admin -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d
   ```

9. **Reinstall ArgoCD** (capstone GitOps bonus) -- it lives inside the AKS
   cluster, installed by hand via `kubectl`, not by Terraform or `deploy.yml`,
   so `terraform destroy` wipes it and it does NOT come back on its own:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts
   kubectl wait --for=condition=available --timeout=180s deployment/argocd-server deployment/argocd-repo-server -n argocd
   kubectl apply -f argocd/monitoring-application.yaml
   kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
   kubectl get svc argocd-server -n argocd   # wait for a new EXTERNAL-IP, update README with it
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
   ```
   Note: use `--server-side --force-conflicts` on the install manifest --
   plain `kubectl apply` fails on `applicationsets.argoproj.io` ("metadata
   .annotations: Too long") because the CRD exceeds the
   last-applied-configuration annotation size limit. The admin password
   regenerates on every fresh install -- re-read it, don't reuse the old one.

## If something goes wrong mid-redeploy

This exact sequence already hit two real issues once, both already fixed in
the committed code -- if either resurfaces it means something upstream
(Azure capacity, a deleted action tag) changed again:
- AKS rejects the configured VM size ("not allowed in your subscription") --
  check `az vm list-skus --location eastus --size <new size>` for an
  available alternative and update `terraform.tfvars`.
- `build` fails at "Set up job" on the Trivy action -- check
  `gh api repos/aquasecurity/trivy-action/tags` for the current tag format
  and update the pin in `.github/workflows/build.yml`.
