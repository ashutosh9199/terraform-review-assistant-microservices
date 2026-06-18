import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_secret
from app.models.domain import Finding, LlmSettings, Report, ReviewJob, ReviewStatus
from app.services import clients


class ReviewOrchestrator:
    """Coordinates a review by calling the downstream microservices over HTTP.

    The gateway holds the database and secrets; each analysis stage runs in its
    own service. This class sequences them and persists the results.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def run(self, review_id: int) -> None:
        job = self.db.get(ReviewJob, review_id)
        if not job:
            return
        job.status = ReviewStatus.running.value
        job.started_at = datetime.now(UTC)
        self.db.commit()
        try:
            source_files = await clients.fetch_source_files(job.id)
            inventory, graph = await clients.parse_project(source_files)
            rule_findings = await clients.evaluate_rules(inventory)
            ai_findings = await clients.ai_review(inventory, graph, rule_findings, self._llm_credentials())
            findings = rule_findings + ai_findings
            scorecard = await clients.score(findings)
            reports = await clients.build_reports(inventory, graph, findings, scorecard)
            json_report = reports["json_report"]

            job.inventory = inventory
            job.dependency_graph = graph
            job.scorecard = scorecard
            job.status = ReviewStatus.completed.value
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
