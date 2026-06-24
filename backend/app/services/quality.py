from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.services.financial_analysis import CalculationResult, MetricValue


@dataclass(frozen=True)
class QualityIssue:
    severity: str
    category: str
    message: str
    needs_human_review: bool


FORBIDDEN_INVESTMENT_LANGUAGE = [
    "buy now",
    "sell now",
    "guaranteed return",
    "必涨",
    "确定上涨",
    "立即买入",
    "立即卖出",
]


def check_data_quality(
    facts: list[MetricValue],
    *,
    as_of: datetime | None = None,
    max_age_days: int = 370,
) -> list[QualityIssue]:
    now = as_of or datetime.now(UTC)
    issues: list[QualityIssue] = []
    seen_metrics: dict[str, MetricValue] = {}

    for fact in facts:
        if fact.value is None:
            issues.append(issue("high", "missing_value", f"{fact.metric} is missing."))
        if fact.currency and len(fact.currency) != 3:
            issues.append(issue("medium", "currency_error", f"{fact.metric} has invalid currency."))
        if not fact.unit:
            issues.append(issue("medium", "unit_error", f"{fact.metric} is missing unit."))
        if not fact.fiscal_period:
            issues.append(issue("medium", "fiscal_period_error", f"{fact.metric} missing period."))
        prior = seen_metrics.get(fact.metric)
        if prior is not None and prior.value != fact.value:
            issues.append(
                issue("high", "source_conflict", f"{fact.metric} has conflicting values.")
            )
        seen_metrics[fact.metric] = fact

    if not facts:
        issues.append(issue("high", "missing_data", "No financial facts supplied."))

    stale_cutoff = now - timedelta(days=max_age_days)
    for fact in facts:
        if "FY" in fact.fiscal_period:
            continue
        if fact.fiscal_period < stale_cutoff.date().isoformat():
            issues.append(issue("medium", "stale_data", f"{fact.metric} may be stale."))
    return issues


def audit_ai_output(
    text: str,
    claims_with_citations: list[bool],
    calculations: list[CalculationResult],
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    lowered = text.lower()
    for phrase in FORBIDDEN_INVESTMENT_LANGUAGE:
        if phrase.lower() in lowered:
            issues.append(
                issue("critical", "investment_promise_language", f"Forbidden phrase: {phrase}")
            )
    if any(not has_citation for has_citation in claims_with_citations):
        issues.append(issue("high", "uncited_claim", "At least one claim lacks citation."))
    if any(result.status == "unavailable" for result in calculations):
        issues.append(
            issue("medium", "calculation_gap", "One or more calculations are unavailable.")
        )
    if "assumption" in lowered and "fact" in lowered:
        issues.append(issue("low", "assumption_fact_boundary", "Review assumption/fact wording."))
    return issues


def backtest_guardrail(
    record_available_at: datetime, model_run_at: datetime
) -> QualityIssue | None:
    if record_available_at > model_run_at:
        return issue(
            "critical", "future_data_leakage", "Record was not available at model run time."
        )
    return None


def estimate_confidence(source_scores: list[Decimal], issue_count: int) -> Decimal:
    if not source_scores:
        return Decimal("0.0000")
    average = sum(source_scores) / Decimal(len(source_scores))
    penalty = Decimal("0.0500") * Decimal(issue_count)
    return max(Decimal("0.0000"), min(Decimal("1.0000"), average - penalty))


def issue(severity: str, category: str, message: str) -> QualityIssue:
    return QualityIssue(
        severity=severity,
        category=category,
        message=message,
        needs_human_review=severity in {"critical", "high"},
    )
