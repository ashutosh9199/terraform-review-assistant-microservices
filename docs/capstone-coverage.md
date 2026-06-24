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
| SAST (static analysis) | `.github/workflows/codeql.yml` (Python + JS/TS) |
| Code quality (lint) | `build.yml` ruff (gateway) + `npm run lint` (frontend) |
| Notification on success/failure | `deploy.yml` notify step (`if: always()`) |
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
| Advanced monitoring (Prometheus + Grafana) | `kubernetes/monitoring/` -- Prometheus scrapes real HTTP metrics from `apps/api-gateway/app/main.py`, Grafana auto-provisions a 3-panel dashboard (request rate by path, request rate by status, p95 latency). Verified live: `sum(http_requests_total)` returns real traffic through Grafana's datasource proxy. Also: Application Insights + Container Insights (`oms_agent`) |
| Network Policy | `kubernetes/networkpolicy.yaml` (includes a scoped cross-namespace rule so Prometheus, in its own `monitoring` namespace, can reach `api-gateway:8000` without widening same-namespace-only ingress) |
| GitOps (ArgoCD, pull-based CD) | `argocd/monitoring-application.yaml` -- ArgoCD installed in-cluster (`argocd` namespace), manages the `monitoring` stack with automated sync + prune + selfHeal direct from this repo's `main` branch. Deliberate hybrid: `production` (image-tag substitution + manual approval gate) stays on push-based CD via `deploy.yml`; the observability stack (fixed public images, no per-deploy secrets) is pull-based GitOps instead. Verified live: `kubectl get application monitoring -n argocd` shows `Synced`/`Healthy`. |

## §5 — Pre-evaluation checklist
| Item | Status |
|---|---|
| Repo shared / all code on main | done — all commits on `main`, share repo access with evaluators before the call |
| No credentials in git history | verified — full `git log --all -p` grepped for secret patterns, clean |
| Terraform validates | verified — `terraform validate`/`fmt` pass locally and in CI (`terraform-apply.yml`) |
| K8s manifests validated | verified — `kubectl apply --dry-run=client` passes against the live cluster |
| Workflows succeed | verified — `terraform-apply`, `build` (all 8 images, Trivy gate clean), and `deploy` each have a recorded successful run with their approval gate exercised |
| App running & accessible | verified live — `http://20.241.214.29/healthz` → `200 OK`; full review pipeline exercised end-to-end (upload → parse → rules → score → report) |
