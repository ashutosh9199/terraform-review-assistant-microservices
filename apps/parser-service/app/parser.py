from pathlib import Path
from typing import Any

import hcl2

SUPPORTED_RESOURCE_TYPES = {
    "azurerm_resource_group",
    "azurerm_virtual_network",
    "azurerm_network_security_group",
    "azurerm_linux_virtual_machine",
    "azurerm_windows_virtual_machine",
    "azurerm_storage_account",
    "azurerm_key_vault",
    "azurerm_kubernetes_cluster",
    "azurerm_mssql_database",
    "azurerm_linux_web_app",
    "azurerm_windows_web_app",
    "azurerm_lb",
    "azurerm_public_ip",
}


class TerraformParserService:
    def parse_project(self, root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        files = sorted([*root.rglob("*.tf"), *root.rglob("*.tfvars")])
        resources: list[dict[str, Any]] = []
        variables: list[dict[str, Any]] = []
        outputs: list[dict[str, Any]] = []
        providers: list[dict[str, Any]] = []
        diagnostics: list[dict[str, str]] = []

        for file_path in files:
            try:
                with file_path.open("r", encoding="utf-8") as handle:
                    parsed = hcl2.load(handle)
            except Exception as exc:
                diagnostics.append({"file": str(file_path), "message": f"Parse failed: {exc}"})
                continue

            for block in parsed.get("resource", []):
                for raw_resource_type, named_blocks in block.items():
                    resource_type = _clean_label(raw_resource_type)
                    for raw_name, attributes in named_blocks.items():
                        name = _clean_label(raw_name)
                        address = f"{resource_type}.{name}"
                        resources.append(
                            {
                                "address": address,
                                "resource_type": resource_type,
                                "name": name,
                                "file": str(file_path.relative_to(root)),
                                "supported": resource_type in SUPPORTED_RESOURCE_TYPES,
                                "attributes": attributes,
                                "tags": attributes.get("tags", {}),
                            }
                        )

            for block in parsed.get("variable", []):
                for raw_name, attributes in block.items():
                    name = _clean_label(raw_name)
                    variables.append({"name": name, "file": str(file_path.relative_to(root)), **attributes})

            for block in parsed.get("output", []):
                for raw_name, attributes in block.items():
                    name = _clean_label(raw_name)
                    outputs.append({"name": name, "file": str(file_path.relative_to(root)), **attributes})

            for block in parsed.get("provider", []):
                for raw_name, attributes in block.items():
                    name = _clean_label(raw_name)
                    providers.append({"name": name, "file": str(file_path.relative_to(root)), **attributes})

        inventory = {
            "files": [str(path.relative_to(root)) for path in files],
            "resource_count": len(resources),
            "resources": resources,
            "variables": variables,
            "outputs": outputs,
            "providers": providers,
            "diagnostics": diagnostics,
        }
        graph = self._build_dependency_graph(resources)
        return inventory, graph

    def _build_dependency_graph(self, resources: list[dict[str, Any]]) -> dict[str, Any]:
        addresses = {resource["address"] for resource in resources}
        edges: list[dict[str, str]] = []
        for resource in resources:
            text = str(resource.get("attributes", {}))
            for candidate in addresses:
                if candidate != resource["address"] and candidate in text:
                    edges.append({"from": resource["address"], "to": candidate})
        return {"nodes": sorted(addresses), "edges": edges}


def _clean_label(value: str) -> str:
    return value.strip().strip('"')
