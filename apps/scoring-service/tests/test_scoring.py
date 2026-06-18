from app.scoring import ScoringService


def test_scoring_deducts_by_severity() -> None:
    score = ScoringService().score(
        [
            {"category": "security", "severity": "critical", "title": "Public admin"},
            {"category": "governance", "severity": "medium", "title": "Missing tag"},
        ]
    )
    assert score["security_score"] == 80
    assert score["governance_score"] == 95
    assert score["overall_score"] < 100
