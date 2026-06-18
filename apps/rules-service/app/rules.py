from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleFinding:
    source: str
    category: str
    severity: str
    resource_address: str | None
    title: str
    description: str
    recommendation: str
    business_impact: str
    terraform_fix: str | None = None
    confidence: int = 100


REQUIRED_TAGS = {"Environment", "Project", "Owner", "CostCenter"}


class RuleEngineService:
    def evaluate(self, inventory: dict[str, Any]) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for resource in inventory.get("resources", []):
            attrs = resource.get("attributes", {})
            address = resource["address"]
            resource_type = resource["resource_type"]
            findings.extend(self._tag_findings(resource, attrs))
            findings.extend(self._naming_findings(resource))

            if resource_type == "azurerm_storage_account":
                findings.extend(self._storage_rules(address, attrs))
            elif resource_type in {"azurerm_linux_virtual_machine", "azurerm_windows_virtual_machine"}:
                findings.extend(self._vm_rules(address, attrs))
            elif resource_type == "azurerm_kubernetes_cluster":
                findings.extend(self._aks_rules(address, attrs))
            elif resource_type == "azurerm_key_vault":
                findings.extend(self._key_vault_rules(address, attrs))
            elif resource_type == "azurerm_network_security_group":
                findings.extend(self._nsg_rules(address, attrs))
            elif resource_type == "azurerm_public_ip":
                findings.extend(self._public_ip_rules(address, attrs))
            elif resource_type == "azurerm_mssql_database":
                findings.extend(self._sql_rules(address, attrs))
            elif resource_type in {"azurerm_linux_web_app", "azurerm_windows_web_app"}:
                findings.extend(self._app_service_rules(address, attrs))

        return findings

    def _tag_findings(self, resource: dict[str, Any], attrs: dict[str, Any]) -> list[RuleFinding]:
        tags = attrs.get("tags") or {}
        missing = sorted(REQUIRED_TAGS.difference(tags.keys()))
        if not missing:
            return []
        return [
            RuleFinding(
                source="rule_engine",
                category="governance",
                severity="medium",
                resource_address=resource["address"],
                title="Required tags are missing",
                description=f"Resource is missing required tags: {', '.join(missing)}.",
                recommendation="Apply enterprise tags for Environment, Project, Owner, and CostCenter.",
                business_impact="Improves ownership, chargeback, policy enforcement, and operational reporting.",
                terraform_fix='tags = { Environment = "dev", Project = "platform", Owner = "team", CostCenter = "cc-001" }',
            )
        ]

    def _naming_findings(self, resource: dict[str, Any]) -> list[RuleFinding]:
        name = resource["name"]
        if name.lower() == name and "_" not in name:
            return []
        return [
            RuleFinding(
                source="rule_engine",
                category="governance",
                severity="low",
                resource_address=resource["address"],
                title="Resource name does not follow baseline naming convention",
                description="Terraform resource names should be lowercase snake-free identifiers.",
                recommendation="Use lowercase alphanumeric names and encode business naming in resource attributes.",
                business_impact="Improves consistency and makes automation easier to maintain.",
            )
        ]

    def _storage_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        if attrs.get("allow_blob_public_access") is True:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "Storage account allows public blob access",
                    "Blob public access is enabled on the storage account.",
                    "Set allow_blob_public_access to false and use private endpoints for sensitive workloads.",
                    "Reduces risk of unauthorized data exposure.",
                    "allow_blob_public_access = false",
                )
            )
        if attrs.get("https_traffic_only_enabled") is False:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "Storage account does not enforce HTTPS",
                    "The storage account permits non-HTTPS traffic.",
                    "Set https_traffic_only_enabled to true.",
                    "Protects data in transit and supports compliance requirements.",
                    "https_traffic_only_enabled = true",
                )
            )
        if attrs.get("min_tls_version") in {None, "TLS1_0", "TLS1_1"}:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "medium",
                    address,
                    "Storage account TLS baseline is weak or missing",
                    "The storage account should require TLS 1.2 or newer.",
                    "Set min_tls_version to TLS1_2.",
                    "Reduces exposure to deprecated cryptographic protocols.",
                    'min_tls_version = "TLS1_2"',
                )
            )
        if "blob_properties" not in attrs:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "medium",
                    address,
                    "Storage account diagnostics and lifecycle posture need review",
                    "The storage account does not define blob service properties in Terraform.",
                    "Configure delete retention, container retention, versioning, and diagnostics for production data.",
                    "Improves recoverability and reduces operational blind spots.",
                )
            )
        return findings

    def _vm_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        if "identity" not in attrs:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "medium",
                    address,
                    "Virtual machine is missing managed identity",
                    "Managed identity is not configured for the VM.",
                    "Use system-assigned or user-assigned managed identity instead of stored credentials.",
                    "Reduces credential leakage risk and simplifies access governance.",
                    'identity { type = "SystemAssigned" }',
                )
            )
        if "boot_diagnostics" not in attrs:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "medium",
                    address,
                    "VM boot diagnostics are missing",
                    "Boot diagnostics are not configured.",
                    "Enable boot diagnostics for supportability.",
                    "Improves troubleshooting during incidents.",
                )
            )
        return findings

    def _aks_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        if attrs.get("role_based_access_control_enabled") is False:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "critical",
                    address,
                    "AKS RBAC is disabled",
                    "The AKS cluster does not enable role-based access control.",
                    "Enable Azure RBAC or Kubernetes RBAC.",
                    "Prevents broad unaudited cluster access.",
                    "role_based_access_control_enabled = true",
                )
            )
        if "oms_agent" not in str(attrs):
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "high",
                    address,
                    "AKS monitoring is missing",
                    "The cluster does not appear to enable Azure Monitor Container Insights.",
                    "Enable the oms_agent add-on and route logs to Log Analytics.",
                    "Improves production observability and incident response.",
                )
            )
        if attrs.get("private_cluster_enabled") is not True:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "AKS cluster is not private",
                    "The AKS API server appears reachable through a public endpoint.",
                    "Enable private_cluster_enabled and access the control plane through private network paths.",
                    "Reduces public control-plane exposure for production clusters.",
                    "private_cluster_enabled = true",
                )
            )
        return findings

    def _key_vault_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        if attrs.get("purge_protection_enabled") is not True:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "Key Vault purge protection is missing",
                    "Purge protection is not enabled.",
                    "Enable purge protection for production Key Vaults.",
                    "Protects keys and secrets from irreversible deletion.",
                    "purge_protection_enabled = true",
                )
            )
        if attrs.get("soft_delete_retention_days") is None:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "governance",
                    "medium",
                    address,
                    "Key Vault soft delete retention is not explicit",
                    "Soft delete retention is not set explicitly.",
                    "Set soft_delete_retention_days according to enterprise policy.",
                    "Makes recovery behavior auditable and predictable.",
                    "soft_delete_retention_days = 90",
                )
            )
        if attrs.get("public_network_access_enabled") is not False:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "Key Vault public network access is enabled",
                    "The Key Vault does not explicitly disable public network access.",
                    "Disable public network access and use private endpoints for production secret stores.",
                    "Limits exposure of high-value secrets and keys to approved network paths.",
                    "public_network_access_enabled = false",
                )
            )
        return findings

    def _nsg_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        text = str(attrs)
        if '"*"' in text and any(port in text for port in ["22", "3389"]):
            return [
                RuleFinding(
                    "rule_engine",
                    "security",
                    "critical",
                    address,
                    "NSG may expose administrative ports to the internet",
                    "The NSG appears to allow SSH or RDP from a broad source.",
                    "Restrict administrative access through Azure Bastion, VPN, or Just-in-Time access.",
                    "Significantly reduces remote compromise risk.",
                )
            ]
        return []

    def _public_ip_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = [
            RuleFinding(
                "rule_engine",
                "security",
                "medium",
                address,
                "Public IP resource requires exposure justification",
                "The Terraform project provisions a public IP address.",
                "Confirm the workload requires public ingress and protect it with WAF, NSG rules, or private alternatives.",
                "Reduces accidental internet exposure and clarifies ownership of externally reachable endpoints.",
            )
        ]
        if attrs.get("sku") != "Standard":
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "medium",
                    address,
                    "Public IP should use Standard SKU",
                    "Basic public IPs have weaker availability and security defaults.",
                    "Use Standard SKU public IPs for production workloads.",
                    "Improves reliability and aligns with Azure production baselines.",
                    'sku = "Standard"',
                )
            )
        return findings

    def _sql_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        sku = str(attrs.get("sku_name", "")).lower()
        if sku and (sku.startswith("p") or "businesscritical" in sku or "hyperscale" in sku):
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "cost",
                    "medium",
                    address,
                    "SQL database SKU may be oversized",
                    "The SQL database uses a high-cost SKU family.",
                    "Validate required DTU/vCore, HA, storage, and latency needs before production approval.",
                    "Prevents recurring database spend from exceeding workload requirements.",
                )
            )
        if attrs.get("zone_redundant") is not True:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "medium",
                    address,
                    "SQL database zone redundancy is not enabled",
                    "The database does not explicitly enable zone redundancy.",
                    "Enable zone_redundant for production tiers where regional availability zone support exists.",
                    "Improves availability for business-critical data services.",
                    "zone_redundant = true",
                )
            )
        return findings

    def _app_service_rules(self, address: str, attrs: dict[str, Any]) -> list[RuleFinding]:
        findings = []
        if attrs.get("https_only") is not True:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "high",
                    address,
                    "App Service does not enforce HTTPS",
                    "The web app does not explicitly require HTTPS-only traffic.",
                    "Set https_only to true and redirect plaintext traffic.",
                    "Protects users and service-to-service traffic from downgrade or interception risks.",
                    "https_only = true",
                )
            )
        if "identity" not in attrs:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "security",
                    "medium",
                    address,
                    "App Service is missing managed identity",
                    "The web app has no managed identity configured.",
                    "Use managed identity for Key Vault, database, and storage access.",
                    "Removes secret-bearing app settings and simplifies access review.",
                    'identity { type = "SystemAssigned" }',
                )
            )
        if "logs" not in attrs:
            findings.append(
                RuleFinding(
                    "rule_engine",
                    "operations",
                    "medium",
                    address,
                    "App Service logging is not configured",
                    "Application and platform logs are not defined in Terraform.",
                    "Enable application logs, HTTP logs, diagnostics, and Application Insights integration.",
                    "Improves incident response and production supportability.",
                )
            )
        return findings
