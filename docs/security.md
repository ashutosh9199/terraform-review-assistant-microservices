# Security

## Upload Handling

- File extensions are restricted to `.tf`, `.tfvars`, and `.zip`
- Upload size is bounded by `MAX_UPLOAD_MB`
- ZIP extraction blocks path traversal
- Terraform is never executed
- Files are isolated per review ID

## Authentication and Authorization

- JWT authentication
- Role-based authorization
- In-memory API rate limiting for local and single-instance deployments
- Default roles: `admin`, `reviewer`
- Admin role required for LLM settings changes

## Secret Handling

- API keys are encrypted before database storage in local development
- In Azure, secrets should be placed in Key Vault
- Secrets are never returned from the settings API

## Audit Logging

The backend writes audit records for:

- Login success/failure
- Uploads
- LLM settings changes

## Production Hardening

Before public production exposure:

- Add enterprise SSO
- Add tenant isolation
- Replace in-memory rate limiting with Redis-backed distributed rate limiting
- Add malware scanning for uploaded ZIP files
- Store reports in Blob Storage with private containers
- Enforce Azure Private Link for database and storage
- Enable Defender for Cloud recommendations
