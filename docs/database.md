# Database Schema

The local implementation uses SQLAlchemy and SQLite. Production deployment should use Azure SQL.

## Tables

### `users`

- `id`
- `email`
- `password_hash`
- `full_name`
- `is_active`

### `user_roles`

- `id`
- `user_id`
- `role`

### `projects`

- `id`
- `name`
- `description`
- `created_by`
- `created_at`

### `review_jobs`

- `id`
- `project_id`
- `status`
- `original_filename`
- `storage_path`
- `created_by`
- `created_at`
- `started_at`
- `completed_at`
- `error_message`
- `inventory`
- `dependency_graph`
- `scorecard`

### `findings`

- `id`
- `review_job_id`
- `source`
- `category`
- `severity`
- `resource_address`
- `title`
- `description`
- `recommendation`
- `business_impact`
- `terraform_fix`
- `confidence`
- `created_at`

### `reports`

- `id`
- `review_job_id`
- `format`
- `content`
- `created_at`

### `llm_settings`

- `id`
- `provider`
- `endpoint`
- `model`
- `encrypted_api_key`
- `is_active`
- `updated_at`

### `audit_logs`

- `id`
- `actor_user_id`
- `action`
- `target`
- `metadata_json`
- `created_at`
