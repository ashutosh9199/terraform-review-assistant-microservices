import base64
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.reporting import ReportingService

app = FastAPI(
    title="Reporting Service",
    version="0.1.0",
    description="Generates JSON, HTML, and PDF review reports.",
)

reporting = ReportingService()


class ReportRequest(BaseModel):
    inventory: dict[str, Any]
    dependency_graph: dict[str, Any]
    findings: list[dict[str, Any]] = []
    scorecard: dict[str, Any]
    executive_feedback: str = ""


@app.get("/healthz", tags=["system"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "reporting-service"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "reporting-service"}


@app.post("/report", tags=["reporting"])
def report(request: ReportRequest) -> dict[str, Any]:
    json_report = reporting.build_json_report(
        request.inventory,
        request.dependency_graph,
        request.findings,
        request.scorecard,
        request.executive_feedback,
    )
    html_report = reporting.build_html_report(json_report)
    pdf_report = reporting.build_pdf_report(json_report)
    return {
        "json_report": json_report,
        "html": html_report,
        "pdf_base64": base64.b64encode(pdf_report).decode("ascii"),
    }
