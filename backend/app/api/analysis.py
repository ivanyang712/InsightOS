from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agents import Citation, EvidenceItem, orchestrate_research_report
from app.services.financial_analysis import (
    CalculationResult,
    MetricValue,
    bull_base_bear_scenarios,
    calculate_financial_quality_metrics,
    dcf_valuation,
    multiple_valuation,
    reverse_dcf_required_growth,
    sensitivity_table,
)
from app.services.quality import audit_ai_output, check_data_quality

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class MetricValuePayload(BaseModel):
    metric: str
    value: Decimal
    currency: str | None = Field(default=None, max_length=3)
    unit: str
    fiscal_period: str
    source_hash: str


class FinancialQualityRequest(BaseModel):
    current: list[MetricValuePayload]
    previous: list[MetricValuePayload] | None = None


class DcfValuationRequest(BaseModel):
    free_cash_flows: list[Decimal]
    discount_rate: Decimal
    terminal_growth_rate: Decimal
    net_debt: Decimal


class MultipleValuationRequest(BaseModel):
    model: str
    numerator_value: Decimal
    denominator_value: Decimal
    multiple: Decimal


class SensitivityRequest(BaseModel):
    base_cash_flows: list[Decimal]
    discount_rates: list[Decimal]
    terminal_growth_rates: list[Decimal]
    net_debt: Decimal


class ReverseDcfRequest(BaseModel):
    target_enterprise_value: Decimal
    base_free_cash_flow: Decimal
    discount_rate: Decimal
    terminal_growth_rate: Decimal
    years: int = Field(default=5, ge=1, le=20)


class ScenarioRequest(BaseModel):
    base_free_cash_flow: Decimal
    growth_rates: dict[str, Decimal]
    years: int = Field(default=3, ge=1, le=20)


class DataQualityRequest(BaseModel):
    facts: list[MetricValuePayload]


class AiOutputAuditRequest(BaseModel):
    text: str
    claims_with_citations: list[bool]
    calculation_statuses: list[str] = Field(default_factory=list)


class CitationPayload(BaseModel):
    source_name: str
    source_url: str
    published_at: str
    retrieved_at: str
    confidence_score: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))


class EvidenceItemPayload(BaseModel):
    id: str
    text: str
    citation: CitationPayload
    fact_value: str | None = None
    formula: str | None = None


class ResearchReportRequest(BaseModel):
    evidence: list[EvidenceItemPayload]


@router.post("/financial-quality")
def calculate_financial_quality(request: FinancialQualityRequest) -> dict[str, object]:
    current = metric_map(request.current)
    previous = metric_map(request.previous or []) if request.previous is not None else None
    return {"metrics": calculate_financial_quality_metrics(current, previous)}


@router.post("/valuation/dcf")
def calculate_dcf(request: DcfValuationRequest) -> dict[str, object]:
    return dcf_valuation(
        request.free_cash_flows,
        request.discount_rate,
        request.terminal_growth_rate,
        request.net_debt,
    )


@router.post("/valuation/multiple")
def calculate_multiple(request: MultipleValuationRequest) -> dict[str, object]:
    return multiple_valuation(
        request.model,
        request.numerator_value,
        request.denominator_value,
        request.multiple,
    )


@router.post("/valuation/sensitivity")
def calculate_sensitivity(request: SensitivityRequest) -> dict[str, object]:
    return {
        "model": "dcf_sensitivity",
        "rows": sensitivity_table(
            request.base_cash_flows,
            request.discount_rates,
            request.terminal_growth_rates,
            request.net_debt,
        ),
        "calculated_at": datetime.now(UTC),
    }


@router.post("/valuation/reverse-dcf")
def calculate_reverse_dcf(request: ReverseDcfRequest) -> dict[str, object]:
    return reverse_dcf_required_growth(
        request.target_enterprise_value,
        request.base_free_cash_flow,
        request.discount_rate,
        request.terminal_growth_rate,
        request.years,
    )


@router.post("/valuation/scenarios")
def calculate_scenarios(request: ScenarioRequest) -> dict[str, object]:
    return {
        "scenarios": bull_base_bear_scenarios(
            request.base_free_cash_flow, request.growth_rates, request.years
        ),
        "calculated_at": datetime.now(UTC),
    }


@router.post("/quality/data")
def run_data_quality(request: DataQualityRequest) -> dict[str, object]:
    return {"issues": check_data_quality(list(metric_map(request.facts).values()))}


@router.post("/quality/ai-output")
def run_ai_output_audit(request: AiOutputAuditRequest) -> dict[str, object]:
    calculations = [
        CalculationResult(
            metric=f"input_calculation_{index}",
            status=status,
            value=None,
            unit="n/a",
            fiscal_period="unknown",
            formula="provided_status",
            inputs={},
            calculated_at=datetime.now(UTC),
        )
        for index, status in enumerate(request.calculation_statuses)
    ]
    return {
        "issues": audit_ai_output(
            request.text,
            request.claims_with_citations,
            calculations,
        )
    }


@router.post("/agents/research-report")
def generate_agent_report(request: ResearchReportRequest) -> dict[str, object]:
    evidence = [
        EvidenceItem(
            id=item.id,
            text=item.text,
            citation=Citation(
                source_name=item.citation.source_name,
                source_url=item.citation.source_url,
                published_at=item.citation.published_at,
                retrieved_at=item.citation.retrieved_at,
                confidence_score=item.citation.confidence_score,
            ),
            fact_value=item.fact_value,
            formula=item.formula,
        )
        for item in request.evidence
    ]
    return orchestrate_research_report(evidence)


def metric_map(items: list[MetricValuePayload]) -> dict[str, MetricValue]:
    return {
        item.metric: MetricValue(
            metric=item.metric,
            value=item.value,
            currency=item.currency,
            unit=item.unit,
            fiscal_period=item.fiscal_period,
            source_hash=item.source_hash,
        )
        for item in items
    }
