# Deployment Guide

## Local

Use Docker Compose:

```powershell
docker compose up --build
```

Or run services separately:

```powershell
cd apps/api-gateway
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
python -m app.bootstrap
uvicorn app.main:app --reload --port 8000
```

```powershell
cd apps/frontend
npm install
npm run dev
```

## Azure Infrastructure

```powershell
cd infra/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

Recommended production values:

- Use Azure SQL instead of local SQLite
- Use Azure Blob Storage for uploads and reports
- Use Key Vault for JWT secret, API keys, and database credentials
- Enable managed identity for App Services
- Restrict CORS to the production frontend URL
- Configure Application Insights connection strings

## GitHub Actions Secrets

Configure repository secrets:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
AZURE_CREDENTIALS
AZURE_RESOURCE_GROUP
API_APP_NAME
FRONTEND_APP_NAME
ACR_LOGIN_SERVER
```

The included workflow validates, tests, scans, builds, and leaves deployment commands as clearly marked steps for your Azure environment.
