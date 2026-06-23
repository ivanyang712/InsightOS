from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceSchema(BaseModel):
    source_name: str
    source_url: str
    published_at: datetime
    retrieved_at: datetime
    currency: str | None = Field(default=None, max_length=3)
    fiscal_period: str | None = None
    confidence_score: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    source_hash: str = Field(min_length=64, max_length=64)
    data_status: str


class ReadSchema(ProvenanceSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(ProvenanceSchema):
    legal_name: str
    display_name: str
    cik: str | None = None
    lei: str | None = None
    headquarters_country: str | None = None
    website_url: str | None = None
    description: str | None = None


class CompanyRead(CompanyCreate, ReadSchema):
    pass


class SecurityCreate(ProvenanceSchema):
    company_id: str
    ticker: str
    exchange: str
    security_type: str
    primary_listing: bool = True
    isin: str | None = None
    cusip: str | None = None


class SecurityRead(SecurityCreate, ReadSchema):
    pass


class SourceDocumentCreate(ProvenanceSchema):
    company_id: str | None = None
    document_type: str
    title: str
    issuer: str | None = None
    document_date: date | None = None
    storage_url: str | None = None
    mime_type: str | None = None
    raw_text_excerpt: str | None = None


class SourceDocumentRead(SourceDocumentCreate, ReadSchema):
    pass


class FilingCreate(ProvenanceSchema):
    company_id: str
    source_document_id: str | None = None
    accession_number: str
    filing_type: str
    filed_at: datetime
    period_end_date: date | None = None
    sec_file_number: str | None = None


class FilingRead(FilingCreate, ReadSchema):
    pass


class FinancialFactCreate(ProvenanceSchema):
    company_id: str
    security_id: str | None = None
    filing_id: str | None = None
    source_document_id: str | None = None
    evidence_chunk_id: str | None = None
    metric_name: str
    statement: str | None = None
    value: Decimal
    unit: str
    scale: Decimal | None = None
    formula: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    as_reported: bool = True


class FinancialFactRead(FinancialFactCreate, ReadSchema):
    pass


class MarketPriceCreate(ProvenanceSchema):
    security_id: str
    price_date: date
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    close_price: Decimal
    adjusted_close_price: Decimal | None = None
    volume: int | None = None


class MarketPriceRead(MarketPriceCreate, ReadSchema):
    pass


class MacroSeriesCreate(ProvenanceSchema):
    series_code: str
    series_name: str
    observation_date: date
    value: Decimal
    unit: str
    frequency: str
    seasonal_adjustment: str | None = None


class MacroSeriesRead(MacroSeriesCreate, ReadSchema):
    pass


class IndustryTaxonomyCreate(ProvenanceSchema):
    taxonomy_name: str
    industry_code: str
    industry_name: str
    parent_industry_id: str | None = None
    level: int
    description: str | None = None


class IndustryTaxonomyRead(IndustryTaxonomyCreate, ReadSchema):
    pass


class CompanyIndustryMappingCreate(ProvenanceSchema):
    company_id: str
    industry_id: str
    classification_type: str
    valid_from: date | None = None
    valid_to: date | None = None


class CompanyIndustryMappingRead(CompanyIndustryMappingCreate, ReadSchema):
    pass


class EvidenceChunkCreate(ProvenanceSchema):
    source_document_id: str
    chunk_index: int
    section_name: str | None = None
    page_number: int | None = None
    start_char: int | None = None
    end_char: int | None = None
    text: str


class EvidenceChunkRead(EvidenceChunkCreate, ReadSchema):
    pass


class ResearchReportCreate(ProvenanceSchema):
    company_id: str
    title: str
    report_type: str
    generated_at: datetime
    model_version: str
    methodology: str
    input_snapshot_hash: str
    report_status: str
    summary: str | None = None


class ResearchReportRead(ResearchReportCreate, ReadSchema):
    pass


class ReportClaimCreate(ProvenanceSchema):
    research_report_id: str
    evidence_chunk_id: str | None = None
    financial_fact_id: str | None = None
    claim_text: str
    claim_type: str
    conclusion_level: str
    formula: str | None = None
    generated_at: datetime
    evidence_summary: str | None = None


class ReportClaimRead(ReportClaimCreate, ReadSchema):
    pass


class AssumptionCreate(ProvenanceSchema):
    company_id: str
    research_report_id: str | None = None
    valuation_model_id: str | None = None
    assumption_name: str
    scenario: str
    numeric_value: Decimal | None = None
    text_value: str | None = None
    unit: str | None = None
    formula: str | None = None
    rationale: str


class AssumptionRead(AssumptionCreate, ReadSchema):
    pass


class ValuationModelCreate(ProvenanceSchema):
    company_id: str
    research_report_id: str | None = None
    model_type: str
    scenario: str
    valuation_date: date
    base_currency: str
    output_metric: str
    output_value: Decimal
    formula: str
    input_snapshot_hash: str
    model_payload: dict[str, Any] | None = None


class ValuationModelRead(ValuationModelCreate, ReadSchema):
    pass


class WatchlistCreate(ProvenanceSchema):
    name: str
    owner_label: str
    description: str | None = None
    visibility: str
    criteria: dict[str, Any] | None = None


class WatchlistRead(WatchlistCreate, ReadSchema):
    pass


class AlertCreate(ProvenanceSchema):
    watchlist_id: str | None = None
    company_id: str | None = None
    security_id: str | None = None
    alert_type: str
    condition: str
    threshold_value: Decimal | None = None
    unit: str | None = None
    is_active: bool = True
    triggered_at: datetime | None = None
    last_evaluated_at: datetime | None = None


class AlertRead(AlertCreate, ReadSchema):
    pass
