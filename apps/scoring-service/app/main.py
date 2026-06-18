from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.scoring import ScoringService

app = FastAPI(
    title="Scoring Service",
    version="0.1.0",
    description="Calculates the weighted infrastructure scorecard from normalized findings.",
)

scoring = ScoringService()


class ScoreRequest(BaseModel):
    findings: list[dict[str, Any]] = []


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "scoring-service"}


@app.post("/score", tags=["scoring"])
def score(request: ScoreRequest) -> dict[str, Any]:
    return scoring.score(request.findings)
