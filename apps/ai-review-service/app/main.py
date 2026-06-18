from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.ai_review import AiReviewService
from app.llm import LlmClient

app = FastAPI(
    title="AI Review Service",
    version="0.1.0",
    description="Runs specialist AI reviewers against deterministic evidence.",
)


class LlmCredentials(BaseModel):
    provider: str
    api_key: str
    endpoint: str | None = None
    model: str | None = None


class ReviewRequest(BaseModel):
    inventory: dict[str, Any]
    dependency_graph: dict[str, Any]
    rule_findings: list[dict[str, Any]] = []
    llm: LlmCredentials | None = None


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "ai-review-service"}


@app.post("/review", tags=["ai"])
async def review(request: ReviewRequest) -> dict[str, object]:
    client: LlmClient | None = None
    if request.llm:
        client = LlmClient(
            provider=request.llm.provider,
            api_key=request.llm.api_key,
            endpoint=request.llm.endpoint,
            model=request.llm.model,
        )
    findings = await AiReviewService(client).review(
        request.inventory,
        request.dependency_graph,
        request.rule_findings,
    )
    return {"findings": findings}
