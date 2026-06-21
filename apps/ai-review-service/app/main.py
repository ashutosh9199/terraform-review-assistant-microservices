from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.ai_review import AiReviewService
from app.llm import LlmClient, LlmError, detect_provider

app = FastAPI(
    title="AI Review Service",
    version="0.1.0",
    description="Runs specialist AI reviewers against deterministic evidence.",
)


class LlmCredentials(BaseModel):
    provider: str | None = None
    api_key: str
    endpoint: str | None = None
    model: str | None = None


class ReviewRequest(BaseModel):
    inventory: dict[str, Any]
    dependency_graph: dict[str, Any]
    rule_findings: list[dict[str, Any]] = []
    llm: LlmCredentials | None = None
    categories: list[str] | None = None


class SynthesizeRequest(BaseModel):
    inventory: dict[str, Any]
    dependency_graph: dict[str, Any]
    findings: list[dict[str, Any]] = []
    scorecard: dict[str, Any]
    llm: LlmCredentials | None = None


def _build_client(llm: LlmCredentials | None) -> LlmClient | None:
    if not llm:
        return None
    return LlmClient(provider=llm.provider, api_key=llm.api_key, endpoint=llm.endpoint, model=llm.model)


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "ai-review-service"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "ai-review-service"}


@app.post("/review", tags=["ai"])
async def review(request: ReviewRequest) -> dict[str, object]:
    findings = await AiReviewService(_build_client(request.llm)).review(
        request.inventory,
        request.dependency_graph,
        request.rule_findings,
        request.categories,
    )
    return {"findings": findings}


@app.post("/synthesize", tags=["ai"])
async def synthesize(request: SynthesizeRequest) -> dict[str, str]:
    """Executive review agent: runs last, with full context of every other agent's output."""
    feedback = await AiReviewService(_build_client(request.llm)).synthesize(
        request.inventory,
        request.dependency_graph,
        request.findings,
        request.scorecard,
    )
    return {"feedback": feedback}


@app.post("/test", tags=["ai"])
async def test_connection(request: LlmCredentials) -> dict[str, str]:
    """Sends a minimal real request to the configured provider and returns its reply.

    Unlike /review and /synthesize, this raises a real error (502) on failure instead
    of silently falling back, so the caller can show the user exactly what went wrong.
    """
    provider = request.provider or detect_provider(request.api_key, request.endpoint, request.model)
    if provider == "unknown":
        raise HTTPException(status_code=400, detail="Could not detect provider from the supplied key/endpoint.")
    client = LlmClient(provider=provider, api_key=request.api_key, endpoint=request.endpoint, model=request.model)
    try:
        reply = await client.test_connection()
    except LlmError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"provider": provider, "model": client.model, "reply": reply}
