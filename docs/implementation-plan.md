# Implementation Plan

This document is the working execution plan for completing the AI-Powered Terraform Review Assistant as a production Azure SaaS platform.

## Current Status

Implemented:

- FastAPI API gateway with JWT authentication, RBAC dependencies, rate limiting, audit logging, projects, reviews, dashboard, and LLM settings.
- Upload workflow for ZIP projects, single Terraform files, and multiple Terraform files.
- Terraform parser for resources, variables, outputs, providers, inventory, diagnostics, and dependency graph.
- Static rule engine for storage accounts, virtual machines, AKS, Key Vault, NSGs, public IPs, SQL databases, App Services, tags, and naming.
- AI review abstraction with provider detection and Azure OpenAI/OpenAI-compatible chat-completions support.
- Scoring service for security, cost, governance, operations, Terraform quality, and overall score.
- Reporting service with JSON, HTML, and PDF exports stored in the database.
- React, TypeScript, Material UI frontend with dashboard, upload, analysis, reports, settings, and login pages.
- Terraform modules for resource group, storage account, SQL database, Key Vault, App Service, monitoring, and Application Insights.
- Dockerfiles, docker-compose, GitHub Actions CI/CD workflow, API docs, deployment docs, database docs, and security docs.

## Execution Phases

### Phase 1: Stabilize MVP

- Run backend dependency installation and tests in a clean Python 3.11 environment.
- Add API integration tests for authentication, project creation, multi-file upload, review completion, and report download.
- Add frontend lint cleanup and at least one smoke test for authenticated navigation.
- Add database migration tooling with Alembic.
- Replace local background tasks with durable job state transitions and retry-safe orchestration.

### Phase 2: Production Azure Foundation

- Wire Azure Blob Storage backend behind the existing `StorageService`.
- Wire Key Vault secret reads/writes for LLM settings and application secrets.
- Add managed identity support for App Service access to Blob, SQL, Key Vault, and Application Insights.
- Add Azure SQL connection configuration and production startup checks.
- Add private networking options for SQL, Storage, Key Vault, and App Service.

### Phase 3: Review Engine Depth

- Expand Terraform parser coverage for modules, data sources, locals, dynamic blocks, and cross-file references.
- Add rule IDs, enabled/disabled flags, organization policy profiles, and rule severity overrides.
- Add Azure Well-Architected rule packs for security, reliability, cost, operational excellence, and governance.
- Add optional Checkov/tfsec ingestion as additional evidence.
- Add Azure Cost Management enrichment for SKU and region-aware cost findings.

### Phase 4: Enterprise SaaS

- Add tenant model, project membership, reviewer/admin roles, and row-level authorization checks.
- Add SSO with Microsoft Entra ID.
- Add report sharing, report retention policies, and audit export.
- Add queue-based microservices split with Azure Service Bus and worker containers.
- Add observability dashboards, alerts, synthetic health checks, and structured logs.

### Phase 5: Delivery Hardening

- Split CI/CD into build, test, security scan, Docker build, Terraform plan, and deploy environments.
- Publish versioned backend/frontend container images.
- Add SBOM generation and dependency vulnerability gates.
- Add deployment runbooks and rollback procedures.
- Add load testing for upload, parse, and report generation paths.

## Next Best Agent Tasks

1. Install backend dev dependencies in Python 3.11 and run `ruff check app tests` and `pytest`.
2. Fix any test failures from the new multi-upload and report-section changes.
3. Add Azure Blob and Key Vault implementations behind the current local abstractions.
4. Add Alembic migrations for all SQLAlchemy models.
5. Add integration tests for a complete upload-to-report review using `examples/insecure-storage`.

