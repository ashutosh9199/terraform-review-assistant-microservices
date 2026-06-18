import json
import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

ANTHROPIC_VERSION = "2023-06-01"
ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-6"
# Stable, generally-available default (per https://ai.google.dev/gemini-api/docs/models).
# Avoid defaulting to -preview models: they're more likely to be excluded from free-tier quota.
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"


def detect_provider(api_key: str, endpoint: str | None = None, model: str | None = None) -> str:
    endpoint_lower = (endpoint or "").lower()
    model_lower = (model or "").lower()
    if "openai.azure.com" in endpoint_lower:
        return "azure_openai"
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if "generativelanguage.googleapis.com" in endpoint_lower or "gemini" in model_lower:
        return "gemini"
    if api_key.startswith("AIza"):
        return "gemini"
    if api_key.startswith("sk-"):
        return "openai"
    if endpoint:
        return "openai_compatible"
    return "unknown"


class LlmError(Exception):
    """Raised when a real call to the configured LLM provider fails.

    Carries the provider's own error text so the UI can show the actual reason
    (auth failure, bad model name, quota, etc.) instead of failing silently.
    """


class LlmClient:
    def __init__(self, provider: str, api_key: str, endpoint: str | None, model: str | None) -> None:
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model or self._default_model()

    def _default_model(self) -> str:
        if self.provider == "anthropic":
            return ANTHROPIC_DEFAULT_MODEL
        if self.provider == "gemini":
            return GEMINI_DEFAULT_MODEL
        return "gpt-4o"

    async def complete_json(self, system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
        """Used during a review run. Never raises: a provider hiccup must not fail the
        whole review, so on error this logs the real cause and falls back to the
        offline heuristic rather than silently pretending nothing happened."""
        if self.provider == "unknown":
            logger.warning("LLM provider could not be determined; using offline heuristic.")
            return self._offline_review(user_payload)
        try:
            text = await self._complete_text(system_prompt, user_payload, want_json=True)
            return _extract_json(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM call to provider=%s failed, falling back to offline heuristic: %s", self.provider, exc)
            return self._offline_review(user_payload)

    async def test_connection(self) -> str:
        """Used by the Settings 'Test' button. Raises LlmError with the provider's
        actual error message on failure instead of swallowing it."""
        if self.provider == "unknown":
            raise LlmError("Could not determine the LLM provider from the supplied key/endpoint.")
        try:
            return await self._complete_text("Reply in one short sentence.", {"message": "hi"}, want_json=False)
        except LlmError:
            raise
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            raise LlmError(f"{self.provider} returned HTTP {exc.response.status_code}: {detail}") from exc
        except httpx.RequestError as exc:
            raise LlmError(f"Could not reach {self.provider} endpoint: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise LlmError(f"Unexpected error calling {self.provider}: {exc}") from exc

    async def _complete_text(self, system_prompt: str, user_payload: dict[str, Any], *, want_json: bool) -> str:
        if self.provider in {"openai", "openai_compatible", "azure_openai"}:
            return await self._openai_text(system_prompt, user_payload, want_json)
        if self.provider == "anthropic":
            return await self._anthropic_text(system_prompt, user_payload)
        if self.provider == "gemini":
            return await self._gemini_text(system_prompt, user_payload, want_json)
        raise LlmError(f"Unsupported provider: {self.provider}")

    async def _openai_text(self, system_prompt: str, user_payload: dict[str, Any], want_json: bool) -> str:
        if self.provider == "azure_openai":
            if not self.endpoint:
                raise LlmError("Azure OpenAI requires an endpoint.")
            base = self.endpoint.rstrip("/")
            url = f"{base}/openai/deployments/{self.model}/chat/completions?api-version=2024-10-21"
            headers = {"api-key": self.api_key}
        else:
            base = (self.endpoint or "https://api.openai.com").rstrip("/")
            url = f"{base}/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            "temperature": 0.2,
        }
        if want_json:
            body["response_format"] = {"type": "json_object"}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    async def _anthropic_text(self, system_prompt: str, user_payload: dict[str, Any]) -> str:
        url = (self.endpoint or "https://api.anthropic.com").rstrip("/") + "/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": json.dumps(user_payload)}],
        }
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            return "".join(block.get("text", "") for block in data.get("content", []))

    async def _gemini_text(self, system_prompt: str, user_payload: dict[str, Any], want_json: bool) -> str:
        # Per https://ai.google.dev/gemini-api/docs/api-key: pass the key via the
        # x-goog-api-key header, not the legacy ?key= query parameter (which also
        # risks the key leaking into proxy/access logs).
        base = (self.endpoint or "https://generativelanguage.googleapis.com").rstrip("/")
        url = f"{base}/v1beta/models/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}
        body: dict[str, Any] = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": json.dumps(user_payload)}]}],
        }
        if want_json:
            body["generationConfig"] = {"responseMimeType": "application/json"}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers=headers, json=body)
            if response.status_code == 429:
                raise LlmError(_gemini_quota_message(self.model, response.text))
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                block_reason = data.get("promptFeedback", {}).get("blockReason")
                if block_reason:
                    raise LlmError(f"Gemini blocked the request: {block_reason}")
                raise LlmError(f"Gemini returned no candidates: {data}")
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(part.get("text", "") for part in parts)

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


def _gemini_quota_message(model: str, raw_error: str) -> str:
    if "limit: 0" in raw_error or "free_tier" in raw_error:
        return (
            f"Gemini rejected the request for model '{model}': this Google Cloud project has a "
            "free-tier quota of 0 for this model (limit: 0), which means the project isn't "
            "enrolled for free-tier access rather than this being a usage issue. Fix options: "
            "(1) generate a new key at https://aistudio.google.com/apikey for a project with "
            "free-tier access enabled, or (2) enable billing on the project at "
            "https://aistudio.google.com/usage to move to the paid tier. "
            f"Raw response: {raw_error[:300]}"
        )
    return f"Gemini rate limit exceeded for model '{model}': {raw_error[:400]}"


def _extract_json(text: str) -> dict[str, Any]:
    """Anthropic and Gemini don't support strict JSON-mode like OpenAI, so the
    reply may include surrounding prose. Try a direct parse, then fall back to
    extracting the first {...} block."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise LlmError(f"Model response was not valid JSON: {text[:200]}")
