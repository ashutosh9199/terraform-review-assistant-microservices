from dataclasses import asdict
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.rules import RuleEngineService

app = FastAPI(
    title="Rule Engine Service",
    version="0.1.0",
    description="Evaluates deterministic Azure governance, security, cost, and operations rules.",
)

engine = RuleEngineService()


class EvaluateRequest(BaseModel):
    inventory: dict[str, Any]


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "rules-service"}


@app.post("/evaluate", tags=["rules"])
def evaluate(request: EvaluateRequest) -> dict[str, object]:
    findings = [asdict(finding) for finding in engine.evaluate(request.inventory)]
    return {"findings": findings}
