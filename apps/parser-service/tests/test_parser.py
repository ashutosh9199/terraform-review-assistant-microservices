from pathlib import Path

from app.parser import TerraformParserService


def test_parser_normalizes_resource_labels() -> None:
    root = Path(__file__).resolve().parents[3] / "examples" / "insecure-storage"
    inventory, graph = TerraformParserService().parse_project(root)

    assert {resource["address"] for resource in inventory["resources"]} == {
        "azurerm_resource_group.rg",
        "azurerm_storage_account.storageDemo",
    }
    assert inventory["resource_count"] == 2
    assert "azurerm_storage_account.storageDemo" in graph["nodes"]
