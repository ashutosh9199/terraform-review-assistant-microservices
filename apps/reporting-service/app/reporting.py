from datetime import UTC, datetime
from io import BytesIO
from typing import Any

from jinja2 import Template

REPORT_TEMPLATE = Template(
    """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Terraform Review Report</title>
  <style>
    body { font-family: Arial, sans-serif; color: #172033; margin: 32px; }
    h1, h2 { color: #0f3b5f; }
    .score { display: inline-block; padding: 10px 14px; background: #eef6f8; margin-right: 8px; }
    .finding { border-top: 1px solid #d7dee8; padding: 12px 0; }
    .severity { font-weight: bold; text-transform: uppercase; }
    code { background: #f3f5f7; padding: 2px 4px; }
  </style>
</head>
<body>
  <h1>Terraform Infrastructure Review</h1>
  <p>Generated at {{ generated_at }}</p>
  <h2>Scorecard</h2>
  <div class="score">Overall: {{ scorecard.overall_score }}</div>
  <div class="score">Security: {{ scorecard.security_score }}</div>
  <div class="score">Cost: {{ scorecard.cost_score }}</div>
  <div class="score">Governance: {{ scorecard.governance_score }}</div>
  <div class="score">Operations: {{ scorecard.operations_score }}</div>
  <h2>Executive Summary</h2>
  <p>{{ summary }}</p>
  {% for section in sections %}
  <h2>{{ section.title }}</h2>
  {% if section.findings %}
  {% for finding in section.findings %}
  <section class="finding">
    <p class="severity">{{ finding.severity }} | {{ finding.category }} | {{ finding.source }}</p>
    <h3>{{ finding.title }}</h3>
    <p><strong>Resource:</strong> <code>{{ finding.resource_address or "N/A" }}</code></p>
    <p>{{ finding.description }}</p>
    <p><strong>Recommendation:</strong> {{ finding.recommendation }}</p>
    <p><strong>Business impact:</strong> {{ finding.business_impact or "N/A" }}</p>
    {% if finding.terraform_fix %}<pre>{{ finding.terraform_fix }}</pre>{% endif %}
  </section>
  {% endfor %}
  {% else %}
  <p>No findings in this category.</p>
  {% endif %}
  {% endfor %}
  <h2>Recommendations</h2>
  <ul>
  {% for recommendation in recommendations %}
    <li>{{ recommendation }}</li>
  {% endfor %}
  </ul>
</body>
</html>
"""
)


class ReportingService:
    def build_json_report(
        self,
        inventory: dict[str, Any],
        dependency_graph: dict[str, Any],
        findings: list[dict[str, Any]],
        scorecard: dict[str, Any],
    ) -> dict[str, Any]:
        critical_high = [f for f in findings if f.get("severity") in {"critical", "high"}]
        sections = self._sections(findings)
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "executive_summary": self._summary(scorecard, len(findings), len(critical_high)),
            "scorecard": scorecard,
            "infrastructure_scorecard": scorecard,
            "inventory": inventory,
            "dependency_graph": dependency_graph,
            "findings": findings,
            "security_findings": sections["security"],
            "cost_findings": sections["cost"],
            "governance_findings": sections["governance"],
            "operational_findings": sections["operations"],
            "recommendations": self._recommendations(findings),
        }

    def build_html_report(self, json_report: dict[str, Any]) -> str:
        return REPORT_TEMPLATE.render(
            generated_at=json_report["generated_at"],
            summary=json_report["executive_summary"],
            scorecard=json_report["scorecard"],
            sections=[
                {"title": "Security Findings", "findings": json_report["security_findings"]},
                {"title": "Cost Findings", "findings": json_report["cost_findings"]},
                {"title": "Governance Findings", "findings": json_report["governance_findings"]},
                {"title": "Operational Findings", "findings": json_report["operational_findings"]},
            ],
            recommendations=json_report["recommendations"],
        )

    def build_pdf_report(self, json_report: dict[str, Any]) -> bytes:
        lines = [
            "Terraform Infrastructure Review",
            f"Generated at {json_report['generated_at']}",
            "",
            f"Overall Score: {json_report['scorecard']['overall_score']}/100",
            f"Security: {json_report['scorecard']['security_score']}/100",
            f"Cost: {json_report['scorecard']['cost_score']}/100",
            f"Governance: {json_report['scorecard']['governance_score']}/100",
            f"Operations: {json_report['scorecard']['operations_score']}/100",
            "",
            "Executive Summary",
            json_report["executive_summary"],
            "",
            "Findings",
        ]
        for section_name in [
            "security_findings",
            "cost_findings",
            "governance_findings",
            "operational_findings",
        ]:
            lines.extend(["", section_name.replace("_", " ").title()])
            section_findings = json_report.get(section_name, [])
            if not section_findings:
                lines.append("No findings in this category.")
            for finding in section_findings[:10]:
                lines.extend(
                    [
                        "",
                        f"{finding.get('severity', 'info').upper()} | {finding.get('category')} | {finding.get('source')}",
                        finding.get("title", ""),
                        f"Resource: {finding.get('resource_address') or 'N/A'}",
                        f"Recommendation: {finding.get('recommendation', '')}",
                    ]
                )
        lines.extend(["", "Recommendations"])
        for recommendation in json_report.get("recommendations", [])[:10]:
            lines.extend(
                [
                    f"- {recommendation}",
                ]
            )
        return _simple_pdf(lines)

    def _summary(self, scorecard: dict[str, Any], total: int, critical_high: int) -> str:
        return (
            f"The reviewed Terraform project scored {scorecard['overall_score']}/100. "
            f"The assessment identified {total} findings, including {critical_high} critical or high risk items. "
            "Prioritize public exposure, identity, encryption, monitoring, and governance gaps before production deployment."
        )

    def _sections(self, findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        return {
            "security": [finding for finding in findings if finding.get("category") == "security"],
            "cost": [finding for finding in findings if finding.get("category") == "cost"],
            "governance": [finding for finding in findings if finding.get("category") == "governance"],
            "operations": [finding for finding in findings if finding.get("category") == "operations"],
        }

    def _recommendations(self, findings: list[dict[str, Any]]) -> list[str]:
        ordered = sorted(
            findings,
            key=lambda finding: {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(
                finding.get("severity", "info"),
                4,
            ),
        )
        recommendations: list[str] = []
        seen: set[str] = set()
        for finding in ordered:
            recommendation = finding.get("recommendation")
            if recommendation and recommendation not in seen:
                recommendations.append(recommendation)
                seen.add(recommendation)
            if len(recommendations) == 10:
                break
        return recommendations or ["No prioritized recommendations were generated."]


def _simple_pdf(lines: list[str]) -> bytes:
    escaped_lines = [_escape_pdf(line[:110]) for line in lines]
    content_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    first = True
    for line in escaped_lines:
        if first:
            content_lines.append(f"({line}) Tj")
            first = False
        else:
            content_lines.append("T*")
            content_lines.append(f"({line}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{index} 0 obj\n".encode("ascii"))
        buffer.write(obj)
        buffer.write(b"\nendobj\n")
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()


def _escape_pdf(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
