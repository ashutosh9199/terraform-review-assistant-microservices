"""Friendly, user-facing labels for each step of the review pipeline.

The orchestrator writes the machine key (e.g. "ai_security") onto the job as it
works; this maps that key to text suitable for display on the Analysis page so
the user can see exactly which stage -- including which individual AI agent --
is currently running.
"""

STAGE_LABELS: dict[str, str] = {
    "queued": "Queued",
    "fetching_files": "Loading uploaded Terraform files",
    "parsing": "Parsing Terraform into a resource inventory",
    "evaluating_rules": "Running the deterministic Azure rule engine",
    "ai_security": "Running AI agent: Security Reviewer",
    "ai_cost": "Running AI agent: Cost (FinOps) Reviewer",
    "ai_governance": "Running AI agent: Governance Reviewer",
    "ai_operations": "Running AI agent: Operations Reviewer",
    "scoring": "Calculating the weighted infrastructure scorecard",
    "synthesizing": "Running AI agent: Executive Reviewer (full-context synthesis)",
    "reporting": "Generating JSON, HTML, and PDF reports",
    "completed": "Completed",
    "failed": "Failed",
}

# Display order for a progress stepper. AI agent stages are listed individually
# so the user can see which specific specialist is currently running.
STAGE_ORDER: list[str] = [
    "fetching_files",
    "parsing",
    "evaluating_rules",
    "ai_security",
    "ai_cost",
    "ai_governance",
    "ai_operations",
    "scoring",
    "synthesizing",
    "reporting",
]


def label_for(stage: str | None) -> str:
    if not stage:
        return STAGE_LABELS["queued"]
    return STAGE_LABELS.get(stage, stage.replace("_", " ").title())
