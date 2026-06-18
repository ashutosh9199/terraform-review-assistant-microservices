from typing import Any

from app.llm import LlmClient

AGENT_PROMPTS = {
    "security": "You are an Azure Cloud Security Architect and Terraform reviewer. Return strict JSON with a findings array.",
    "cost": "You are a FinOps Engineer reviewing Azure Terraform. Return strict JSON with a findings array.",
    "governance": "You are an Azure Governance Architect reviewing policy, tags, and naming. Return strict JSON with a findings array.",
    "operations": "You are a Principal DevOps Engineer reviewing observability, resilience, and operations. Return strict JSON with a findings array.",
}

SYNTHESIS_PROMPT = (
    "You are the Lead Reviewer on an Azure Terraform review board. You have the full "
    "context of every specialist reviewer's output: the parsed inventory, the deterministic "
    "rule findings, all AI specialist findings (security, cost, governance, operations), and "
    "the final weighted scorecard. Write one executive feedback paragraph of approximately "
    "100 words summarizing the overall posture, the most material risks, and whether the "
    "project is ready to move forward. Return strict JSON: {\"feedback\": \"<paragraph>\"}."
)


class AiReviewService:
    def __init__(self, llm_client: LlmClient | None) -> None:
        self.llm_client = llm_client

    async def review(
        self,
        inventory: dict[str, Any],
        dependency_graph: dict[str, Any],
        rule_findings: list[dict[str, Any]],
        categories: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Runs the specialist reviewer(s). When `categories` is given (e.g. a single
        ["security"]), only that agent runs -- this lets the caller invoke one agent
        per request so it can report which specific agent is currently executing."""
        if not self.llm_client:
            return []
        normalized: list[dict[str, Any]] = []
        selected = {c: AGENT_PROMPTS[c] for c in categories} if categories else AGENT_PROMPTS
        for category, prompt in selected.items():
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

    async def synthesize(
        self,
        inventory: dict[str, Any],
        dependency_graph: dict[str, Any],
        findings: list[dict[str, Any]],
        scorecard: dict[str, Any],
    ) -> str:
        """Final-pass executive reviewer with full context of every prior agent's output.

        Runs after scoring (not alongside the specialist reviewers) so it can comment on
        the actual overall score and complete finding set, not a partial view.
        """
        if not self.llm_client:
            return self._offline_feedback(findings, scorecard)
        payload = {
            "inventory": inventory,
            "dependency_graph": dependency_graph,
            "findings": findings,
            "scorecard": scorecard,
            "instructions": [
                "Write exactly one paragraph, about 100 words.",
                "Reference the overall score and the most material risks across categories.",
                "State a clear readiness recommendation.",
            ],
        }
        result = await self.llm_client.complete_json(SYNTHESIS_PROMPT, payload)
        feedback = result.get("feedback")
        if not feedback:
            return self._offline_feedback(findings, scorecard)
        return str(feedback)

    def _offline_feedback(self, findings: list[dict[str, Any]], scorecard: dict[str, Any]) -> str:
        critical_high = [f for f in findings if f.get("severity") in {"critical", "high"}]
        top_titles = ", ".join(f["title"] for f in critical_high[:3]) or "no critical or high risk items"
        overall = scorecard.get("overall_score", 0)
        readiness = "ready for staged rollout" if overall >= 80 else "not yet ready for production"
        return (
            f"This review scored {overall}/100 overall across security, cost, governance, and "
            f"operations. Out of {len(findings)} total findings, {len(critical_high)} are critical "
            f"or high risk, most notably: {top_titles}. Security and identity gaps carry the "
            "greatest business impact and should be remediated first, followed by governance and "
            f"operational observability items. Based on the current posture, the project is {readiness}. "
            "Configure an LLM provider in Settings for a deeper, model-generated executive review."
        )
