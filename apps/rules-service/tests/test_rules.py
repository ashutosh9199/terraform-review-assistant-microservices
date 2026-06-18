from app.rules import RuleEngineService

INVENTORY = {
    "resources": [
        {
            "address": "azurerm_storage_account.storageDemo",
            "resource_type": "azurerm_storage_account",
            "name": "storageDemo",
            "attributes": {
                "allow_blob_public_access": True,
                "https_traffic_only_enabled": False,
            },
            "tags": {},
        }
    ]
}


def test_rules_flag_insecure_storage() -> None:
    findings = RuleEngineService().evaluate(INVENTORY)
    titles = {finding.title for finding in findings}

    assert "Storage account allows public blob access" in titles
    assert "Storage account does not enforce HTTPS" in titles
    assert "Required tags are missing" in titles
