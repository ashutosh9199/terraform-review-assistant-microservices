from typing import Any

SEVERITY_DEDUCTION = {
    "critical": 20,
    "high": 10,
    "medium": 5,
    "low": 2,
    "info": 0,
}

CATEGORIES = ["security", "cost", "governance", "operations", "terraform_quality"]
WEIGHTS = {
    "security": 0.35,
    "cost": 0.20,
    "governance": 0.20,
    "operations": 0.15,
    "terraform_quality": 0.10,
}


class ScoringService:
    def score(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        category_scores: dict[str, int] = {}
        reasons: dict[str, list[str]] = {}
        for category in CATEGORIES:
            category_findings = [f for f in findings if f.get("category") == category]
            deduction = sum(SEVERITY_DEDUCTION.get(f.get("severity", "info"), 0) for f in category_findings)
            category_scores[category] = max(0, 100 - deduction)
            reasons[category] = [
                f"{f.get('severity', 'info').upper()}: {f.get('title')}" for f in category_findings[:8]
            ]
        overall = round(sum(category_scores[c] * WEIGHTS[c] for c in CATEGORIES))
        return {
            "overall_score": overall,
            "security_score": category_scores["security"],
            "cost_score": category_scores["cost"],
            "governance_score": category_scores["governance"],
            "operations_score": category_scores["operations"],
            "terraform_quality_score": category_scores["terraform_quality"],
            "reasoning": reasons,
        }
