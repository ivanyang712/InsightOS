from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast

from app.connectors import ConnectorError
from app.connectors.sec import (
    NormalizedFiling,
    NormalizedFinancialFact,
    SecConnector,
    normalize_company_facts,
    normalize_filings,
)
from app.services.archetypes import match_company_archetype
from app.services.data_ingestion import raw_record_from_response
from app.services.financial_analysis import (
    CalculationResult,
    MetricValue,
    bull_base_bear_scenarios,
    calculate_financial_quality_metrics,
    dcf_valuation,
    unavailable_payload,
)
from app.services.quality import audit_ai_output, check_data_quality, estimate_confidence

TICKER_TO_CIK = {
    "AAPL": "0000320193",
    "NVDA": "0001045810",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "KO": "0000021344",
    "JPM": "0000019617",
}

SEC_TO_ENGINE_METRICS = {
    "revenues": "revenue",
    "gross_profit": "gross_profit",
    "operating_income": "operating_income",
    "net_income": "net_income",
    "cash": "cash",
    "current_assets": "current_assets",
    "current_liabilities": "current_liabilities",
    "shareholders_equity": "shareholders_equity",
    "operating_cash_flow": "operating_cash_flow",
    "capital_expenditure": "capital_expenditure",
    "shares_outstanding": "shares_outstanding",
}

DEBT_COMPONENTS = {"debt_current", "long_term_debt_noncurrent"}


class UnsupportedTickerError(ValueError):
    pass


@dataclass(frozen=True)
class FinancialInputSnapshot:
    current: dict[str, MetricValue]
    previous: dict[str, MetricValue] | None
    latest_year: int | None
    previous_year: int | None
    latest_period: str
    normalized_facts: list[NormalizedFinancialFact]


def run_single_company_research(
    ticker: str,
    *,
    connector: SecConnector | None = None,
) -> dict[str, object]:
    normalized_ticker = ticker.upper().strip()
    cik = TICKER_TO_CIK.get(normalized_ticker)
    if cik is None:
        raise UnsupportedTickerError(
            f"{normalized_ticker} is not in the MVP ticker map. "
            "Try AAPL, NVDA, MSFT, GOOGL, AMZN, KO, or JPM."
        )

    sec = connector or SecConnector()
    profile_response = sec.get_company_profile(cik)
    facts_response = sec.get_company_facts(cik)
    filings = normalize_filings(cik, profile_response.payload)
    normalized_facts = normalize_company_facts(facts_response)
    snapshot = build_financial_input_snapshot(normalized_facts)
    calculations = calculate_financial_quality_metrics(snapshot.current, snapshot.previous)
    quality_issues = check_data_quality(list(snapshot.current.values())) + audit_ai_output(
        "This report avoids personalized trading instructions and guaranteed-return language.",
        [True, True, True],
        calculations,
    )
    valuation = build_valuation(snapshot.current)
    archetype = match_company_archetype(
        normalized_ticker,
        str(profile_response.payload.get("sicDescription") or ""),
    )
    confidence = estimate_confidence(
        [
            Decimal(str(profile_response.metadata.confidence_score)),
            Decimal(str(facts_response.metadata.confidence_score)),
        ],
        len(quality_issues),
    )

    profile = {
        "name": profile_response.payload.get("name")
        or profile_response.payload.get("entityName")
        or normalized_ticker,
        "ticker": normalized_ticker,
        "cik": cik,
        "sic": profile_response.payload.get("sic"),
        "sic_description": profile_response.payload.get("sicDescription"),
        "archetype": archetype,
    }
    sources = [
        source_summary(
            "company_profile",
            profile_response.metadata.source_name,
            profile_response.metadata.source_url,
            profile_response.metadata.published_at,
            profile_response.metadata.retrieved_at,
            profile_response.metadata.source_hash,
            Decimal(str(profile_response.metadata.confidence_score)),
        ),
        source_summary(
            "company_facts",
            facts_response.metadata.source_name,
            facts_response.metadata.source_url,
            facts_response.metadata.published_at,
            facts_response.metadata.retrieved_at,
            facts_response.metadata.source_hash,
            Decimal(str(facts_response.metadata.confidence_score)),
        ),
    ]

    return {
        "ticker": normalized_ticker,
        "status": "completed",
        "generated_at": datetime.now(UTC),
        "data_source": "SEC EDGAR / SEC XBRL",
        "company": profile,
        "latest_annual_period": snapshot.latest_period,
        "filings": [filing_to_dict(filing) for filing in filings[:8]],
        "raw_records": [
            raw_record_from_response("sec", profile_response, normalized_status="profile_loaded"),
            raw_record_from_response("sec", facts_response, normalized_status="facts_normalized"),
        ],
        "normalized_facts": [
            fact_to_dict(fact)
            for fact in sorted(
                snapshot.normalized_facts,
                key=lambda item: (item.fiscal_year or 0, item.metric_name),
                reverse=True,
            )[:24]
        ],
        "financial_inputs": {
            "current": metric_values_to_payload(snapshot.current),
            "previous": metric_values_to_payload(snapshot.previous or {}),
        },
        "financial_quality": calculations,
        "valuation": valuation,
        "research_report": build_report_sections(profile, calculations, valuation, sources),
        "quality_issues": quality_issues,
        "confidence_score": confidence,
        "sources": sources,
        "limitations": build_limitations(calculations, valuation),
    }


def build_financial_input_snapshot(
    facts: list[NormalizedFinancialFact],
) -> FinancialInputSnapshot:
    annual_facts = [
        fact
        for fact in facts
        if fact.fiscal_year is not None and fact.fiscal_period.endswith("-FY")
    ]
    years = sorted({fact.fiscal_year for fact in annual_facts if fact.fiscal_year is not None})
    latest_year = years[-1] if years else None
    previous_year = years[-2] if len(years) > 1 else None
    current = metrics_for_year(annual_facts, latest_year)
    previous = metrics_for_year(annual_facts, previous_year) if previous_year is not None else None
    latest_period = f"FY{latest_year}" if latest_year is not None else "unknown"
    return FinancialInputSnapshot(
        current=current,
        previous=previous,
        latest_year=latest_year,
        previous_year=previous_year,
        latest_period=latest_period,
        normalized_facts=annual_facts,
    )


def metrics_for_year(
    facts: list[NormalizedFinancialFact],
    fiscal_year: int | None,
) -> dict[str, MetricValue]:
    if fiscal_year is None:
        return {}

    year_facts = [fact for fact in facts if fact.fiscal_year == fiscal_year]
    metrics: dict[str, MetricValue] = {}
    for sec_metric, engine_metric in SEC_TO_ENGINE_METRICS.items():
        fact = latest_fact(year_facts, sec_metric)
        if fact is not None:
            metrics[engine_metric] = metric_value(engine_metric, fact)

    debt_facts = [fact for fact in year_facts if fact.metric_name in DEBT_COMPONENTS]
    if debt_facts:
        total_debt = sum((fact.value for fact in debt_facts), Decimal("0"))
        first = debt_facts[0]
        metrics["total_debt"] = MetricValue(
            metric="total_debt",
            value=total_debt,
            currency=currency_from_unit(first.unit),
            unit=first.unit,
            fiscal_period=first.fiscal_period,
            source_hash=":".join(fact.source_hash for fact in debt_facts),
        )

    operating_cash_flow = metrics.get("operating_cash_flow")
    capital_expenditure = metrics.get("capital_expenditure")
    if operating_cash_flow is not None and capital_expenditure is not None:
        metrics["free_cash_flow"] = MetricValue(
            metric="free_cash_flow",
            value=operating_cash_flow.value - capital_expenditure.value,
            currency=operating_cash_flow.currency,
            unit=operating_cash_flow.unit,
            fiscal_period=operating_cash_flow.fiscal_period,
            source_hash=f"{operating_cash_flow.source_hash}:{capital_expenditure.source_hash}",
        )

    return metrics


def latest_fact(
    facts: list[NormalizedFinancialFact],
    metric_name: str,
) -> NormalizedFinancialFact | None:
    candidates = [fact for fact in facts if fact.metric_name == metric_name]
    if not candidates:
        return None
    return max(candidates, key=lambda fact: fact.filed_at or "")


def metric_value(metric: str, fact: NormalizedFinancialFact) -> MetricValue:
    return MetricValue(
        metric=metric,
        value=fact.value,
        currency=currency_from_unit(fact.unit),
        unit=fact.unit,
        fiscal_period=fact.fiscal_period,
        source_hash=fact.source_hash,
    )


def currency_from_unit(unit: str) -> str | None:
    return unit if len(unit) == 3 and unit.isalpha() else None


def build_valuation(current: dict[str, MetricValue]) -> dict[str, object]:
    free_cash_flow = current.get("free_cash_flow")
    if free_cash_flow is None:
        return {
            "status": "partial",
            "dcf": unavailable_payload("dcf", "Missing free cash flow."),
            "scenarios": {},
            "assumptions": {},
        }

    growth_rates = {
        "bear": Decimal("0.00"),
        "base": Decimal("0.03"),
        "bull": Decimal("0.06"),
    }
    scenarios = bull_base_bear_scenarios(free_cash_flow.value, growth_rates)
    total_debt = current.get("total_debt")
    cash = current.get("cash")
    net_debt = Decimal("0")
    if total_debt is not None and cash is not None:
        net_debt = total_debt.value - cash.value

    return {
        "status": "completed",
        "dcf": {
            scenario: dcf_valuation(cash_flows, Decimal("0.10"), Decimal("0.025"), net_debt)
            for scenario, cash_flows in scenarios.items()
        },
        "scenarios": scenarios,
        "assumptions": {
            "bear_growth": "0% FCF CAGR for three years",
            "base_growth": "3% FCF CAGR for three years",
            "bull_growth": "6% FCF CAGR for three years",
            "discount_rate": "10%",
            "terminal_growth_rate": "2.5%",
            "note": "Assumptions are editable placeholders, not investment advice.",
        },
    }


def build_report_sections(
    profile: dict[str, object],
    calculations: list[CalculationResult],
    valuation: dict[str, object],
    sources: list[dict[str, object]],
) -> dict[str, object]:
    company_name = str(profile["name"])
    ok_calculations = [calculation for calculation in calculations if calculation.status == "ok"]
    assumptions = valuation.get("assumptions")
    assumption_values = (
        [str(value) for value in cast(dict[str, object], assumptions).values()]
        if isinstance(assumptions, dict)
        else []
    )
    return {
        "facts": [
            f"{company_name} is resolved from SEC company submissions.",
            "Financial facts are normalized from SEC XBRL companyfacts.",
        ],
        "calculations": [
            f"{calculation.metric}: {calculation.formula}" for calculation in ok_calculations[:8]
        ],
        "assumptions": assumption_values,
        "interpretation": [
            "The report is a deterministic first-pass research packet.",
            "Unavailable metrics are left unavailable rather than estimated.",
        ],
        "risks": [
            "Filings may not provide every operating metric required for this archetype.",
            "Valuation output is sensitive to placeholder growth and discount-rate assumptions.",
        ],
        "open_questions": [
            "Review the latest 10-K text for segment, customer, and supply-chain disclosures.",
            "Add market price data before using PE, PS, or EV-based multiples.",
        ],
        "sources": sources,
    }


def build_limitations(
    calculations: list[CalculationResult], valuation: dict[str, object]
) -> list[str]:
    limitations = [
        "No personalized buy/sell advice is generated.",
        "Market price data is not connected yet, so trading multiples are not produced.",
    ]
    unavailable = [
        calculation.metric for calculation in calculations if calculation.status == "unavailable"
    ]
    if unavailable:
        limitations.append(
            "Metrics unavailable from current normalized SEC facts: " + ", ".join(unavailable[:8])
        )
    if valuation.get("status") == "partial":
        limitations.append("DCF is unavailable until free cash flow can be calculated.")
    return limitations


def source_summary(
    source_type: str,
    source_name: str,
    source_url: str,
    published_at: datetime,
    retrieved_at: datetime,
    source_hash: str,
    confidence_score: Decimal,
) -> dict[str, object]:
    return {
        "source_type": source_type,
        "source_name": source_name,
        "source_url": source_url,
        "published_at": published_at,
        "retrieved_at": retrieved_at,
        "source_hash": source_hash,
        "confidence_score": confidence_score,
    }


def filing_to_dict(filing: NormalizedFiling) -> dict[str, object]:
    return {
        "accession_number": filing.accession_number,
        "filing_type": filing.filing_type,
        "filed_at": filing.filed_at,
        "period_end_date": filing.period_end_date,
        "primary_document_url": filing.primary_document_url,
    }


def fact_to_dict(fact: NormalizedFinancialFact) -> dict[str, object]:
    return {
        "metric_name": fact.metric_name,
        "value": fact.value,
        "unit": fact.unit,
        "fiscal_period": fact.fiscal_period,
        "fiscal_year": fact.fiscal_year,
        "filed_at": fact.filed_at,
        "source_url": fact.source_url,
        "source_hash": fact.source_hash,
    }


def metric_values_to_payload(values: dict[str, MetricValue]) -> dict[str, dict[str, object]]:
    return {
        key: {
            "metric": value.metric,
            "value": value.value,
            "currency": value.currency,
            "unit": value.unit,
            "fiscal_period": value.fiscal_period,
            "source_hash": value.source_hash,
        }
        for key, value in values.items()
    }


def research_error_payload(ticker: str, error: ConnectorError) -> dict[str, object]:
    return {
        "ticker": ticker.upper(),
        "status": "error",
        "message": str(error),
        "generated_at": datetime.now(UTC),
    }
