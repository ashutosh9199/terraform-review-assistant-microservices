"""HTTP clients for the downstream review microservices.

The gateway owns the database, auth, and secrets. It orchestrates a review by
calling each stateless service over HTTP and persisting the results.
"""

from typing import Any

import httpx

from app.core.config import get_settings


class ServiceError(Exception):
    """Raised when a downstream service returns an error.

    Carries the upstream status code and detail so the API layer can surface
    meaningful messages (e.g. upload validation failures) back to the client.
    """

    def __init__(self, service: str, status_code: int, detail: str) -> None:
        super().__init__(f"{service} returned {status_code}: {detail}")
        self.service = service
        self.status_code = status_code
        self.detail = detail


def _settings():
    return get_settings()


def _raise_for_status(service: str, response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text
    raise ServiceError(service, response.status_code, str(detail))


async def store_upload(review_id: int, files: list[tuple[str, bytes, str]]) -> dict[str, Any]:
    """Forward uploaded files to the upload-service for validation and storage."""
    settings = _settings()
    multipart = [("files", (name, content, content_type)) for name, content, content_type in files]
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(
            f"{settings.upload_service_url}/uploads/{review_id}",
            files=multipart,
        )
    _raise_for_status("upload-service", response)
    return response.json()


async def fetch_source_files(review_id: int) -> list[dict[str, str]]:
    settings = _settings()
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.get(f"{settings.upload_service_url}/uploads/{review_id}/files")
    _raise_for_status("upload-service", response)
    return response.json()["files"]


async def parse_project(files: list[dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
    settings = _settings()
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(
            f"{settings.parser_service_url}/parse",
            json={"files": files},
        )
    _raise_for_status("parser-service", response)
    data = response.json()
    return data["inventory"], data["dependency_graph"]


async def evaluate_rules(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    settings = _settings()
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(
            f"{settings.rules_service_url}/evaluate",
            json={"inventory": inventory},
        )
    _raise_for_status("rules-service", response)
    return response.json()["findings"]


async def ai_review(
    inventory: dict[str, Any],
    dependency_graph: dict[str, Any],
    rule_findings: list[dict[str, Any]],
    llm: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    settings = _settings()
    payload = {
        "inventory": inventory,
        "dependency_graph": dependency_graph,
        "rule_findings": rule_findings,
        "llm": llm,
    }
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(f"{settings.ai_review_service_url}/review", json=payload)
    _raise_for_status("ai-review-service", response)
    return response.json()["findings"]


async def score(findings: list[dict[str, Any]]) -> dict[str, Any]:
    settings = _settings()
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(
            f"{settings.scoring_service_url}/score",
            json={"findings": findings},
        )
    _raise_for_status("scoring-service", response)
    return response.json()


async def build_reports(
    inventory: dict[str, Any],
    dependency_graph: dict[str, Any],
    findings: list[dict[str, Any]],
    scorecard: dict[str, Any],
) -> dict[str, Any]:
    settings = _settings()
    payload = {
        "inventory": inventory,
        "dependency_graph": dependency_graph,
        "findings": findings,
        "scorecard": scorecard,
    }
    async with httpx.AsyncClient(timeout=settings.service_timeout_seconds) as client:
        response = await client.post(f"{settings.reporting_service_url}/report", json=payload)
    _raise_for_status("reporting-service", response)
    return response.json()
