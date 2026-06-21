# Capstone Coverage Map — Track B (Azure AKS)

Every rubric requirement mapped to the file(s) that satisfy it. Paths are repo-relative.

## §A — Infrastructure as Code (Terraform) — 25%
| Requirement | Where |
|---|---|
| Virtual Network with public + private subnets | `infra/terraform/modules/network/` |
| AKS cluster v1.29+, system & user node pools, autoscaling | `infra/terraform/modules/aks/main.tf` |
| Managed cloud service reachable from pods | `infra/terraform/modules/storage-account/` (Blob) |
| Managed Identity for pod auth | `infra/terraform/modules/workload-identity/` |
| Azure Container Registry | `infra/terraform/modules/acr/` |
| Application Insights monitoring | `infra/terraform/modules/application-insights/` + AKS `oms_agent` |
| Remote state in Storage Account with locking | `environments/aks/backend.tf` + `scripts/bootstrap-tfstate.sh` |
| Modular structure (network/aks/database/storage) | `infra/terraform/modules/*` |
| `terraform validate` & `fmt` pass | `terraform-apply.yml` (validate job); `fmt` verified locally |
| No hardcoded values; `terraform.tfvars` | `environments/aks/terraform.tfvars` |
| All resources tagged Environment + Owner | `var.tags` threaded through every module |
| `.gitignore` excludes `*.tfstate` & secrets | `.gitignore` |
| Outputs document cluster endpoints | `environments/aks/outputs.tf` |

## §B — Kubernetes Deployment — 25%
| Requirement | Where |
|---|---|
| `production` namespace (not default) | `kubernetes/namespace.yaml` |
| ≥2 microservices, >1 replica each | `kubernetes/deployment.yaml` (frontend=2, upload-service=2) |
| Service: LoadBalancer / Ingress | `kubernetes/service.yaml` (frontend LoadBalancer) |
| ConfigMap (non-sensitive env) | `kubernetes/configmap.yaml` |
| Secrets in K8s Secret (not ConfigMap) | `kubernetes/secret.example.yaml` + created by `deploy.yml` |
| ServiceAccount linked to Workload Identity | `kubernetes/serviceaccount.yaml` (upload-service) |
| Liveness `/healthz` + readiness `/ready` | `kubernetes/deployment.yaml`; app endpoints in every `app/main.py` |
| Resource limits within bounds | `kubernetes/deployment.yaml` (cpu 100m/500m, mem 128Mi/512Mi) |
| Manifest organization | `kubernetes/{namespace,serviceaccount,configmap,deployment,service}.yaml` |
| `kubectl apply --dry-run` passes | run in `deploy.yml` |

## §C — GitHub Actions CI/CD — 25%
| Requirement | Where |
|---|---|
| Build pipeline (lint/test/build/scan/push) | `.github/workflows/build.yml` |
| Image scan + fail on HIGH/CRITICAL (gate) | `build.yml` Trivy step (`exit-code: 1`) |
| Deploy pipeline (creds, apply, rollout, smoke) | `.github/workflows/deploy.yml` |
| Deploy requires approval | `deploy.yml` `environment: production` (required reviewers) |
| Infra pipeline (validate/plan/approve/apply) | `.github/workflows/terraform-apply.yml` |
| No credentials in logs / GitHub Secrets | OIDC (`azure/login`), `ARM_USE_OIDC`; secrets referenced, never echoed |

## §D — Cloud Integration / Workload Identity — 25%
| Requirement | Where |
|---|---|
| Managed identity via Terraform | `modules/workload-identity/main.tf` |
| Federated credential linking pod→identity | `azurerm_federated_identity_credential` (same file) |
| ServiceAccount annotated with client-id | `kubernetes/serviceaccount.yaml` |
| App reads/writes cloud service | `apps/upload-service/app/storage.py` (`BlobUploadStore`) |
| No access-key credentials anywhere | `DefaultAzureCredential` only; ConfigMap has account name, no keys |

## §7 — Security & Code Quality (mandatory)
| Requirement | Where |
|---|---|
| No hardcoded credentials | OIDC + Workload Identity + K8s Secret from GitHub Secret |
| Container not root | every `apps/*/Dockerfile` (`USER appuser`/nginx-unprivileged) + `runAsNonRoot` |
| Multistage Docker builds | every `apps/*/Dockerfile` (builder + runtime) |
| Image scanning before deploy | `build.yml` Trivy gate |
| Secrets in K8s Secrets | `kubernetes/secret.example.yaml` |
| RBAC minimal | `kubernetes/serviceaccount.yaml` (no role bindings); pods drop ALL caps |
| `.gitignore` complete | `.gitignore` |

## §8 — Bonus
| Bonus | Where |
|---|---|
| AI integration | core app (`apps/ai-review-service`) |
| API documentation | FastAPI `/docs` (every service) |
| Advanced monitoring | Application Insights + Container Insights (`oms_agent`) |
| Network Policy | `kubernetes/networkpolicy.yaml` |

## §5 — Pre-evaluation checklist
| Item | Status |
|---|---|
| Repo shared / all code on main | after push |
| No credentials in git history | verified by secret audit (see `docs/aks-deployment.md`) |
| Terraform validates | `terraform-apply.yml` |
| K8s manifests validated | `deploy.yml` dry-run |
| Workflows succeed | after secrets/variables configured |
| App running & accessible | frontend LoadBalancer EXTERNAL-IP |
