import json
from typing import Any

import httpx


def detect_provider(api_key: str, endpoint: str | None = None, model: str | None = None) -> str:
    endpoint_lower = (endpoint or "").lower()
    model_lower = (model or "").lower()
    if "openai.azure.com" in endpoint_lower:
        return "azure_openai"
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if "generativelanguage.googleapis.com" in endpoint_lower or "gemini" in model_lower:
        return "gemini"
    if api_key.startswith("sk-"):
        return "openai"
    if endpoint:
        return "openai_compatible"
    return "unknown"


class LlmClient:
    def __init__(self, provider: str, api_key: str, endpoint: str | None, model: str | None) -> None:
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model or "gpt-4o"

    async def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        if self.provider == "unknown":
            return self._offline_review(user_payload)
        try:
            if self.provider in {"openai", "openai_compatible", "azure_openai"}:
                return await self._openai_json(system_prompt, user_payload)
        except Exception:
            return self._offline_review(user_payload)
        return self._offline_review(user_payload)

    async def _openai_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        if self.provider == "azure_openai":
            if not self.endpoint:
                return self._offline_review(user_payload)
            base = self.endpoint.rstrip("/")
            url = f"{base}/openai/deployments/{self.model}/chat/completions?api-version=2024-10-21"
            headers = {"api-key": self.api_key}
        else:
            base = (self.endpoint or "https://api.openai.com").rstrip("/")
            url = f"{base}/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)

    def _offline_review(self, payload: dict[str, Any]) -> dict[str, Any]:
        category = payload.get("category", "governance")
        findings = []
        for resource in payload.get("inventory", {}).get("resources", [])[:3]:
            if not resource.get("supported", True):
                findings.append(
                    {
                        "category": category,
                        "severity": "info",
                        "resource_address": resource["address"],
                        "title": "Resource type needs manual validation",
                        "description": "The parser found a resource outside the current Azure rule catalog.",
                        "recommendation": "Add organization-specific rules or validate this resource manually.",
                        "business_impact": "Keeps review coverage transparent while the rules catalog grows.",
                        "terraform_fix": None,
                        "confidence": 60,
                    }
                )
        return {"findings": findings}
