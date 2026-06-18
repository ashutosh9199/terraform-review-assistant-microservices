"""End-to-end smoke test: drives a full review through the gateway and the six
microservices. Exits non-zero on any failure. Intended for local verification.
"""

import sys
import time
from pathlib import Path

import httpx

GW = "http://127.0.0.1:8000"
EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "insecure-storage" / "main.tf"


def main() -> int:
    tf_bytes = EXAMPLE.read_bytes()

    # Health of every component.
    health = {
        "gateway": f"{GW}/healthz",
        "upload": "http://127.0.0.1:8001/healthz",
        "parser": "http://127.0.0.1:8002/healthz",
        "rules": "http://127.0.0.1:8003/healthz",
        "ai-review": "http://127.0.0.1:8004/healthz",
        "scoring": "http://127.0.0.1:8005/healthz",
        "reporting": "http://127.0.0.1:8006/healthz",
    }
    for name, url in health.items():
        r = httpx.get(url, timeout=10)
        print(f"health {name:10} -> {r.status_code} {r.json()}")
        r.raise_for_status()

    # Login.
    r = httpx.post(
        f"{GW}/api/auth/login",
        json={"email": "admin@example.com", "password": "ChangeMe123!"},
        timeout=30,
    )
    r.raise_for_status()
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    print("login OK")

    # Create project.
    r = httpx.post(f"{GW}/api/projects", json={"name": "Verify Project"}, headers=headers, timeout=30)
    r.raise_for_status()
    project_id = r.json()["id"]
    print(f"project created id={project_id}")

    # Upload + start review.
    files = {"file": ("main.tf", tf_bytes, "text/plain")}
    r = httpx.post(
        f"{GW}/api/reviews/upload?project_id={project_id}",
        files=files,
        headers=headers,
        timeout=60,
    )
    r.raise_for_status()
    review_id = r.json()["id"]
    print(f"review started id={review_id} status={r.json()['status']}")

    # Poll for completion.
    data = {}
    for _ in range(60):
        r = httpx.get(f"{GW}/api/reviews/{review_id}", headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data["status"] in ("completed", "failed"):
            break
        time.sleep(1)

    print(f"final status={data['status']} error={data.get('error_message')}")
    print(f"findings={len(data['findings'])} score={(data.get('scorecard') or {}).get('overall_score')}")

    if data["status"] != "completed":
        print("FAIL: review did not complete")
        return 1
    if not data["findings"]:
        print("FAIL: no findings produced")
        return 1

    # Reports.
    for fmt in ("report.json", "report.html", "report.pdf"):
        rr = httpx.get(f"{GW}/api/reviews/{review_id}/{fmt}", headers=headers, timeout=30)
        print(f"{fmt:12} -> {rr.status_code} ({len(rr.content)} bytes)")
        rr.raise_for_status()

    titles = {f["title"] for f in data["findings"]}
    assert "Storage account allows public blob access" in titles, "expected security finding missing"
    print("E2E OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
