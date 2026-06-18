# Terraform Infrastructure

This stack deploys the Azure foundation for the Terraform Review Assistant.

## Modules

- `resource-group`
- `storage-account`
- `sql-database`
- `key-vault`
- `app-service`
- `monitoring`
- `application-insights`

## Usage

```powershell
cd infra/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

Use environment-specific variable files for production.
