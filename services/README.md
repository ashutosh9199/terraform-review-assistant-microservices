# Microservice Boundaries

The six bounded contexts now run as independent, separately deployable FastAPI
services under `apps/`. The gateway (`apps/api-gateway`) owns the database,
authentication, and secrets; it orchestrates a review by calling each service
over HTTP.

| Service | Path | Port | Responsibility |
|---|---|---|---|
| Upload Service | `apps/upload-service` | 8001 | Validate, store, and expand uploaded Terraform |
| Terraform Parser Service | `apps/parser-service` | 8002 | Parse HCL into inventory + dependency graph |
| Rule Engine Service | `apps/rules-service` | 8003 | Deterministic Azure security/cost/governance/operations rules |
| AI Review Service | `apps/ai-review-service` | 8004 | Specialist LLM reviewers over deterministic evidence |
| Scoring Service | `apps/scoring-service` | 8005 | Weighted infrastructure scorecard |
| Reporting Service | `apps/reporting-service` | 8006 | JSON / HTML / PDF report generation |

## Contracts

- `POST upload-service /uploads/{review_id}` (multipart) → stores files
- `GET  upload-service /uploads/{review_id}/files` → `{ files: [{ path, content }] }`
- `POST parser-service /parse` `{ files: [{ path, content }] }` → `{ inventory, dependency_graph }`
- `POST rules-service /evaluate` `{ inventory }` → `{ findings: [...] }`
- `POST ai-review-service /review` `{ inventory, dependency_graph, rule_findings, llm }` → `{ findings: [...] }`
- `POST scoring-service /score` `{ findings }` → scorecard
- `POST reporting-service /report` `{ inventory, dependency_graph, findings, scorecard }` → `{ json_report, html, pdf_base64 }`

Every service also exposes `GET /healthz`.

## Notes

- Findings keep a stable normalized shape across services, so the gateway can
  persist static and AI findings together and the frontend never changes.
- The gateway decrypts LLM credentials and passes them to the AI Review Service
  per request; the analysis services hold no secrets and no database.
- Next steps toward production: replace synchronous HTTP orchestration with
  Azure Service Bus messages, and store intermediate artifacts in Azure Blob
  Storage and Azure SQL.
