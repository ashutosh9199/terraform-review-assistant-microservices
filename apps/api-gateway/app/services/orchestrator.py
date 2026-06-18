import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_secret
from app.models.domain import Finding, LlmSettings, Report, ReviewJob, ReviewStatus
from app.services import clients

AI_AGENT_CATEGORIES = ["security", "cost", "governance", "operations"]


class ReviewOrchestrator:
    """Coordinates a review by calling the downstream microservices over HTTP.

    The gateway holds the database and secrets; each analysis stage runs in its
    own service. This class sequences them and persists the results, writing
    `job.current_stage` before each step so a polling client can show exactly
    which stage -- including which individual AI agent -- is running right now.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _set_stage(self, job: ReviewJob, stage: str) -> None:
        job.current_stage = stage
        self.db.commit()

    async def run(self, review_id: int) -> None:
        job = self.db.get(ReviewJob, review_id)
        if not job:
            return
        job.status = ReviewStatus.running.value
        job.started_at = datetime.now(UTC)
        self.db.commit()
        try:
            llm_credentials = self._llm_credentials()

            self._set_stage(job, "fetching_files")
            source_files = await clients.fetch_source_files(job.id)

            self._set_stage(job, "parsing")
            inventory, graph = await clients.parse_project(source_files)

            self._set_stage(job, "evaluating_rules")
            rule_findings = await clients.evaluate_rules(inventory)

            # Each specialist agent is called separately (not one batched call) so the
            # current_stage written here reflects which specific AI agent is running.
            ai_findings: list[dict] = []
            for category in AI_AGENT_CATEGORIES:
                self._set_stage(job, f"ai_{category}")
                ai_findings.extend(
                    await clients.ai_review(inventory, graph, rule_findings, llm_credentials, categories=[category])
                )

            findings = rule_findings + ai_findings

            self._set_stage(job, "scoring")
            scorecard = await clients.score(findings)

            # Executive review agent runs last so it has full context of every other
            # agent's output: inventory, all findings, and the final scorecard.
            self._set_stage(job, "synthesizing")
            executive_feedback = await clients.synthesize_review(
                inventory, graph, findings, scorecard, llm_credentials
            )

            self._set_stage(job, "reporting")
            reports = await clients.build_reports(inventory, graph, findings, scorecard, executive_feedback)
            json_report = reports["json_report"]

            job.inventory = inventory
            job.dependency_graph = graph
            job.scorecard = scorecard
            job.executive_feedback = executive_feedback
            job.status = ReviewStatus.completed.value
            job.current_stage = "completed"
            job.completed_at = datetime.now(UTC)
            self.db.query(Finding).filter(Finding.review_job_id == job.id).delete()
            for finding in findings:
                self.db.add(Finding(review_job_id=job.id, **finding))
            self.db.query(Report).filter(Report.review_job_id == job.id).delete()
            self.db.add(Report(review_job_id=job.id, format="json", content=json.dumps(json_report, indent=2)))
            self.db.add(Report(review_job_id=job.id, format="html", content=reports["html"]))
            self.db.add(Report(review_job_id=job.id, format="pdf", content=reports["pdf_base64"]))
            self.db.commit()
        except Exception as exc:
            job.status = ReviewStatus.failed.value
            job.current_stage = "failed"
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            self.db.commit()

    def _llm_credentials(self) -> dict[str, str | None] | None:
        settings = self.db.scalar(select(LlmSettings).where(LlmSettings.is_active.is_(True)))
        if not settings:
            return None
        return {
            "provider": settings.provider,
            "api_key": decrypt_secret(settings.encrypted_api_key),
            "endpoint": settings.endpoint,
            "model": settings.model,
        }
