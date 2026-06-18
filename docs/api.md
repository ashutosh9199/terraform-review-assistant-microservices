# API Documentation

Interactive OpenAPI docs are available at:

```text
http://localhost:8000/docs
```

## Authentication

### POST `/api/auth/login`

Request:

```json
{
  "email": "admin@example.com",
  "password": "ChangeMe123!"
}
```

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "roles": ["admin", "reviewer"]
}
```

Use the token as:

```text
Authorization: Bearer <token>
```

## Projects

### POST `/api/projects`

Creates a project.

### GET `/api/projects`

Lists projects owned by the current user.

## Reviews

### POST `/api/reviews/upload?project_id=1`

Multipart upload fields:

```text
files
```

Supported extensions:

```text
.zip, .tf, .tfvars
```

Send multiple `files` fields to review several Terraform files together. The legacy single `file` field is still accepted for older clients.

### GET `/api/dashboard/summary`

Returns score averages, total reviews, recent reviews, and trend series:

```json
{
  "total_reviews": 12,
  "average_score": 83,
  "security_trend": [{ "label": "17 Jun", "score": 82 }],
  "cost_trend": [{ "label": "17 Jun", "score": 90 }]
}
```

### GET `/api/reviews/{review_id}`

Returns status, inventory, scorecard, and findings.

### GET `/api/reviews/{review_id}/report.json`

Downloads the JSON report.

### GET `/api/reviews/{review_id}/report.html`

Views the HTML report.

### GET `/api/reviews/{review_id}/report.pdf`

Downloads the PDF report.

## Settings

### GET `/api/settings/llm`

Returns active non-secret LLM configuration.

### PUT `/api/settings/llm`

Request:

```json
{
  "api_key": "secret",
  "endpoint": "https://resource.openai.azure.com",
  "model": "gpt-4o",
  "provider": "azure_openai"
}
```

`provider` is optional. If omitted, the backend attempts detection.
