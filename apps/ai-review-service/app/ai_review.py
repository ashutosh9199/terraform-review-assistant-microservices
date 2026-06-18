from typing import Any

from app.llm import LlmClient

AGENT_PROMPTS = {
    "security": "You are an Azure Cloud Security Architect and Terraform reviewer. Return strict JSON with a findings array.",
    "cost": "You are a FinOps Engineer reviewing Azure Terraform. Return strict JSON with a findings array.",
    "governance": "You are an Azure Governance Architect reviewing policy, tags, and naming. Return strict JSON with a findings array.",
    "operations": "You are a Principal DevOps Engineer reviewing observability, resilience, and operations. Return strict JSON with a findings array.",
}


class AiReviewService:
    def __init__(self, llm_client: LlmClient | None) -> None:
        self.llm_client = llm_client

    async def review(
        self,
        inventory: dict[str, Any],
        dependency_graph: dict[str, Any],
        rule_findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not self.llm_client:
            return []
        normalized: list[dict[str, Any]] = []
        for category, prompt in AGENT_PROMPTS.items():
            payload = {
                "category": category,
                "inventory": inventory,
                "dependency_graph": dependency_graph,
                "rule_findings": rule_findings,
                "instructions": [
                    "Identify only materially useful findings.",
                    "Each finding must include severity, recommendation, business impact, and confidence.",
                    "Provide Terraform remediation snippets when possible.",
                ],
            }
            result = await self.llm_client.complete_json(prompt, payload)
            for finding in result.get("findings", []):
                normalized.append(
                    {
                        "source": "ai",
                        "category": finding.get("category", category),
                        "severity": finding.get("severity", "info"),
                        "resource_address": finding.get("resource_address"),
                        "title": finding.get("title", "AI recommendation"),
                        "description": finding.get("description", ""),
                        "recommendation": finding.get("recommendation", ""),
                        "business_impact": finding.get("business_impact"),
                        "terraform_fix": finding.get("terraform_fix"),
                        "confidence": int(float(finding.get("confidence", 70))),
                    }
                )
        return normalized
