from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, EvidenceModelMixin


class Company(EvidenceModelMixin, Base):
    __tablename__ = "companies"

    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cik: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    lei: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    headquarters_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    securities: Mapped[list[Security]] = relationship(back_populates="company")
    filings: Mapped[list[Filing]] = relationship(back_populates="company")
    financial_facts: Mapped[list[FinancialFact]] = relationship(back_populates="company")
    industry_mappings: Mapped[list[CompanyIndustryMapping]] = relationship(back_populates="company")
    research_reports: Mapped[list[ResearchReport]] = relationship(back_populates="company")
    assumptions: Mapped[list[Assumption]] = relationship(back_populates="company")
    valuation_models: Mapped[list[ValuationModel]] = relationship(back_populates="company")
    alerts: Mapped[list[Alert]] = relationship(back_populates="company")


class Security(EvidenceModelMixin, Base):
    __tablename__ = "securities"
    __table_args__ = (UniqueConstraint("ticker", "exchange", name="uq_securities_ticker_exchange"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    security_type: Mapped[str] = mapped_column(String(64), nullable=False)
    primary_listing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    isin: Mapped[str | None] = mapped_column(String(12), nullable=True)
    cusip: Mapped[str | None] = mapped_column(String(9), nullable=True)

    company: Mapped[Company] = relationship(back_populates="securities")
    market_prices: Mapped[list[MarketPrice]] = relationship(back_populates="security")
    financial_facts: Mapped[list[FinancialFact]] = relationship(back_populates="security")
    alerts: Mapped[list[Alert]] = relationship(back_populates="security")


class SourceDocument(EvidenceModelMixin, Base):
    __tablename__ = "source_documents"

    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    storage_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_text_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company | None] = relationship()
    filings: Mapped[list[Filing]] = relationship(back_populates="source_document")
    evidence_chunks: Mapped[list[EvidenceChunk]] = relationship(back_populates="source_document")


class Filing(EvidenceModelMixin, Base):
    __tablename__ = "filings"
    __table_args__ = (UniqueConstraint("accession_number", name="uq_filings_accession_number"),)

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    source_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_documents.id"), nullable=True
    )
    accession_number: Mapped[str] = mapped_column(String(64), nullable=False)
    filing_type: Mapped[str] = mapped_column(String(32), nullable=False)
    filed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sec_file_number: Mapped[str | None] = mapped_column(String(64), nullable=True)

    company: Mapped[Company] = relationship(back_populates="filings")
    source_document: Mapped[SourceDocument | None] = relationship(back_populates="filings")
    financial_facts: Mapped[list[FinancialFact]] = relationship(back_populates="filing")


class FinancialFact(EvidenceModelMixin, Base):
    __tablename__ = "financial_facts"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "metric_name",
            "fiscal_period",
            "source_hash",
            name="uq_financial_facts_metric_period_source",
        ),
    )

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    security_id: Mapped[str | None] = mapped_column(ForeignKey("securities.id"), nullable=True)
    filing_id: Mapped[str | None] = mapped_column(ForeignKey("filings.id"), nullable=True)
    source_document_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_documents.id"), nullable=True
    )
    evidence_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidence_chunks.id"), nullable=True
    )
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    statement: Mapped[str | None] = mapped_column(String(64), nullable=True)
    value: Mapped[Decimal] = mapped_column(Numeric(24, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    scale: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    as_reported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company: Mapped[Company] = relationship(back_populates="financial_facts")
    security: Mapped[Security | None] = relationship(back_populates="financial_facts")
    filing: Mapped[Filing | None] = relationship(back_populates="financial_facts")
    source_document: Mapped[SourceDocument | None] = relationship()
    evidence_chunk: Mapped[EvidenceChunk | None] = relationship(back_populates="financial_facts")
    report_claims: Mapped[list[ReportClaim]] = relationship(back_populates="financial_fact")


class MarketPrice(EvidenceModelMixin, Base):
    __tablename__ = "market_prices"
    __table_args__ = (
        UniqueConstraint(
            "security_id", "price_date", "source_hash", name="uq_prices_security_date_source"
        ),
    )

    security_id: Mapped[str] = mapped_column(ForeignKey("securities.id"), nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    high_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    low_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    close_price: Mapped[Decimal] = mapped_column(Numeric(24, 6), nullable=False)
    adjusted_close_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    volume: Mapped[int | None] = mapped_column(Integer, nullable=True)

    security: Mapped[Security] = relationship(back_populates="market_prices")


class MacroSeries(EvidenceModelMixin, Base):
    __tablename__ = "macro_series"
    __table_args__ = (
        UniqueConstraint(
            "series_code",
            "observation_date",
            "source_hash",
            name="uq_macro_series_observation_source",
        ),
    )

    series_code: Mapped[str] = mapped_column(String(64), nullable=False)
    series_name: Mapped[str] = mapped_column(String(255), nullable=False)
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(24, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(64), nullable=False)
    frequency: Mapped[str] = mapped_column(String(32), nullable=False)
    seasonal_adjustment: Mapped[str | None] = mapped_column(String(64), nullable=True)


class IndustryTaxonomy(EvidenceModelMixin, Base):
    __tablename__ = "industry_taxonomy"
    __table_args__ = (
        UniqueConstraint("taxonomy_name", "industry_code", name="uq_industry_taxonomy_code"),
    )

    taxonomy_name: Mapped[str] = mapped_column(String(64), nullable=False)
    industry_code: Mapped[str] = mapped_column(String(64), nullable=False)
    industry_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_industry_id: Mapped[str | None] = mapped_column(
        ForeignKey("industry_taxonomy.id"), nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_industry: Mapped[IndustryTaxonomy | None] = relationship(
        remote_side=lambda: IndustryTaxonomy.id
    )
    company_mappings: Mapped[list[CompanyIndustryMapping]] = relationship(back_populates="industry")


class CompanyIndustryMapping(EvidenceModelMixin, Base):
    __tablename__ = "company_industry_mapping"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "industry_id",
            "classification_type",
            name="uq_company_industry_classification",
        ),
    )

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    industry_id: Mapped[str] = mapped_column(ForeignKey("industry_taxonomy.id"), nullable=False)
    classification_type: Mapped[str] = mapped_column(String(64), nullable=False)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    company: Mapped[Company] = relationship(back_populates="industry_mappings")
    industry: Mapped[IndustryTaxonomy] = relationship(back_populates="company_mappings")


class EvidenceChunk(EvidenceModelMixin, Base):
    __tablename__ = "evidence_chunks"
    __table_args__ = (
        UniqueConstraint("source_document_id", "chunk_index", name="uq_chunks_document_index"),
    )

    source_document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    source_document: Mapped[SourceDocument] = relationship(back_populates="evidence_chunks")
    financial_facts: Mapped[list[FinancialFact]] = relationship(back_populates="evidence_chunk")
    report_claims: Mapped[list[ReportClaim]] = relationship(back_populates="evidence_chunk")


class ResearchReport(EvidenceModelMixin, Base):
    __tablename__ = "research_reports"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_version: Mapped[str] = mapped_column(String(120), nullable=False)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    report_status: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship(back_populates="research_reports")
    report_claims: Mapped[list[ReportClaim]] = relationship(back_populates="research_report")
    assumptions: Mapped[list[Assumption]] = relationship(back_populates="research_report")
    valuation_models: Mapped[list[ValuationModel]] = relationship(back_populates="research_report")


class ReportClaim(EvidenceModelMixin, Base):
    __tablename__ = "report_claims"

    research_report_id: Mapped[str] = mapped_column(
        ForeignKey("research_reports.id"), nullable=False
    )
    evidence_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("evidence_chunks.id"), nullable=True
    )
    financial_fact_id: Mapped[str | None] = mapped_column(
        ForeignKey("financial_facts.id"), nullable=True
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(64), nullable=False)
    conclusion_level: Mapped[str] = mapped_column(String(64), nullable=False)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    research_report: Mapped[ResearchReport] = relationship(back_populates="report_claims")
    evidence_chunk: Mapped[EvidenceChunk | None] = relationship(back_populates="report_claims")
    financial_fact: Mapped[FinancialFact | None] = relationship(back_populates="report_claims")


class Assumption(EvidenceModelMixin, Base):
    __tablename__ = "assumptions"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    research_report_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_reports.id"), nullable=True
    )
    valuation_model_id: Mapped[str | None] = mapped_column(
        ForeignKey("valuation_models.id"), nullable=True
    )
    assumption_name: Mapped[str] = mapped_column(String(120), nullable=False)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False)
    numeric_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    text_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    company: Mapped[Company] = relationship(back_populates="assumptions")
    research_report: Mapped[ResearchReport | None] = relationship(back_populates="assumptions")
    valuation_model: Mapped[ValuationModel | None] = relationship(back_populates="assumptions")


class ValuationModel(EvidenceModelMixin, Base):
    __tablename__ = "valuation_models"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    research_report_id: Mapped[str | None] = mapped_column(
        ForeignKey("research_reports.id"), nullable=True
    )
    model_type: Mapped[str] = mapped_column(String(64), nullable=False)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    output_metric: Mapped[str] = mapped_column(String(120), nullable=False)
    output_value: Mapped[Decimal] = mapped_column(Numeric(24, 6), nullable=False)
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    model_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    company: Mapped[Company] = relationship(back_populates="valuation_models")
    research_report: Mapped[ResearchReport | None] = relationship(back_populates="valuation_models")
    assumptions: Mapped[list[Assumption]] = relationship(back_populates="valuation_model")


class Watchlist(EvidenceModelMixin, Base):
    __tablename__ = "watchlists"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[str] = mapped_column(String(32), nullable=False)
    criteria: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    alerts: Mapped[list[Alert]] = relationship(back_populates="watchlist")


class Alert(EvidenceModelMixin, Base):
    __tablename__ = "alerts"

    watchlist_id: Mapped[str | None] = mapped_column(ForeignKey("watchlists.id"), nullable=True)
    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    security_id: Mapped[str | None] = mapped_column(ForeignKey("securities.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)
    threshold_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_evaluated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    watchlist: Mapped[Watchlist | None] = relationship(back_populates="alerts")
    company: Mapped[Company | None] = relationship(back_populates="alerts")
    security: Mapped[Security | None] = relationship(back_populates="alerts")


class RawDataRecord(EvidenceModelMixin, Base):
    __tablename__ = "raw_data_records"
    __table_args__ = (
        UniqueConstraint(
            "connector_name", "request_url", "source_hash", name="uq_raw_connector_url_hash"
        ),
    )

    connector_name: Mapped[str] = mapped_column(String(64), nullable=False)
    request_url: Mapped[str] = mapped_column(Text, nullable=False)
    request_params: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    normalized_status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class DataUpdateLog(EvidenceModelMixin, Base):
    __tablename__ = "data_update_logs"

    connector_name: Mapped[str] = mapped_column(String(64), nullable=False)
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_identifier: Mapped[str] = mapped_column(String(120), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    records_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_written: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
