from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.services.agents import (
    Citation,
    EvidenceItem,
    detect_conflicting_evidence,
    orchestrate_research_report,
)
from app.services.financial_analysis import MetricValue
from app.services.quality import (
    audit_ai_output,
    backtest_guardrail,
    check_data_quality,
    estimate_confidence,
)


def test_agent_report_separates_sections_and_citations() -> None:
    citation = Citation(
        source_name="Demo Source",
        source_url="https://example.com/source",
        published_at="2026-01-01",
        retrieved_at="2026-06-23T00:00:00Z",
        confidence_score=Decimal("0.9500"),
    )
    report = orchestrate_research_report(
        [
            EvidenceItem(
                id="e1",
                text="Data center revenue increased in the demo fixture.",
                citation=citation,
            )
        ]
    )

    assert report["facts"]
    assert report["citations"]
    assert report["risks"]
    assert report["open_questions"]
    assert report["confidence_score"] == Decimal("0.9500")


def test_conflicting_evidence_detection() -> None:
    citation = Citation("Demo", "https://example.com", "2026-01-01", "2026-06-23", Decimal("0.9"))
    conflicts = detect_conflicting_evidence(
        [
            EvidenceItem("a", "revenue", citation, fact_value="100"),
            EvidenceItem("b", "revenue", citation, fact_value="101"),
        ]
    )

    assert conflicts == ["revenue"]


def test_quality_checks_for_forbidden_language_and_backtest_leakage() -> None:
    issues = audit_ai_output("This is not buy now language? buy now", [True], [])
    guardrail = backtest_guardrail(datetime.now(UTC) + timedelta(days=1), datetime.now(UTC))

    assert any(issue.category == "investment_promise_language" for issue in issues)
    assert guardrail is not None
    assert guardrail.category == "future_data_leakage"


def test_data_quality_conflicts_and_confidence_penalty() -> None:
    facts = [
        MetricValue("revenue", Decimal("100"), "USD", "USD_millions", "FY2025", "hash1"),
        MetricValue("revenue", Decimal("101"), "USD", "USD_millions", "FY2025", "hash2"),
    ]
    issues = check_data_quality(facts)
    confidence = estimate_confidence([Decimal("0.9"), Decimal("0.8")], len(issues))

    assert any(issue.category == "source_conflict" for issue in issues)
    assert confidence < Decimal("0.8500")
