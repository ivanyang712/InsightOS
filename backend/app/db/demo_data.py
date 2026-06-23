from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from hashlib import sha256

from sqlalchemy.orm import Session

from app.db.base import DataStatus
from app.models import (
    Alert,
    Assumption,
    Company,
    CompanyIndustryMapping,
    EvidenceChunk,
    Filing,
    FinancialFact,
    IndustryTaxonomy,
    MacroSeries,
    MarketPrice,
    ReportClaim,
    ResearchReport,
    Security,
    SourceDocument,
    ValuationModel,
    Watchlist,
)


def hash_source(*parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()


def provenance(
    source_url: str,
    *,
    currency: str | None = "USD",
    fiscal_period: str | None = None,
    confidence_score: Decimal = Decimal("0.9500"),
    payload: str = "",
) -> dict[str, object]:
    published_at = datetime(2026, 1, 15, 13, 30, tzinfo=UTC)
    retrieved_at = datetime(2026, 6, 23, 1, 0, tzinfo=UTC)
    return {
        "source_name": "InsightOS Demo Fixture",
        "source_url": source_url,
        "published_at": published_at,
        "retrieved_at": retrieved_at,
        "currency": currency,
        "fiscal_period": fiscal_period,
        "confidence_score": confidence_score,
        "source_hash": hash_source(source_url, published_at.isoformat(), payload),
        "data_status": DataStatus.ACTIVE.value,
    }


def seed_demo_data(session: Session) -> dict[str, str]:
    company = Company(
        id="demo-company-excs",
        legal_name="Example Cloud Systems Inc.",
        display_name="Example Cloud",
        cik="0000000001",
        lei="EXAMPLELEICODE0001",
        headquarters_country="US",
        website_url="https://example.com/mock/example-cloud",
        description="Mock US-listed infrastructure software company used only for tests.",
        **provenance(
            "https://example.com/mock/company-profile/excs",
            fiscal_period="FY2025",
            payload="company-profile",
        ),
    )
    security = Security(
        id="demo-security-excs",
        company_id=company.id,
        ticker="EXCS",
        exchange="NASDAQ",
        security_type="common_stock",
        primary_listing=True,
        isin="US0000000001",
        cusip="000000001",
        **provenance(
            "https://example.com/mock/security-master/excs",
            fiscal_period="FY2025",
            payload="security-master",
        ),
    )
    source_document = SourceDocument(
        id="demo-source-document-10k",
        company_id=company.id,
        document_type="10-K",
        title="Example Cloud Systems FY2025 Form 10-K",
        issuer="Example Cloud Systems Inc.",
        document_date=date(2026, 1, 15),
        storage_url="mock://source-documents/excs-2025-10k.txt",
        mime_type="text/plain",
        raw_text_excerpt="Revenue was 1200 million USD and gross profit was 720 million USD.",
        **provenance(
            "https://example.com/mock/sec/excs/2025-10-k",
            fiscal_period="FY2025",
            payload="source-document",
        ),
    )
    filing = Filing(
        id="demo-filing-10k",
        company_id=company.id,
        source_document_id=source_document.id,
        accession_number="0000000001-26-000001",
        filing_type="10-K",
        filed_at=datetime(2026, 1, 15, 13, 30, tzinfo=UTC),
        period_end_date=date(2025, 12, 31),
        sec_file_number="001-00001",
        **provenance(
            "https://example.com/mock/sec/excs/2025-10-k",
            fiscal_period="FY2025",
            payload="filing",
        ),
    )
    chunk = EvidenceChunk(
        id="demo-evidence-chunk-revenue",
        source_document_id=source_document.id,
        chunk_index=1,
        section_name="Management Discussion and Analysis",
        page_number=42,
        start_char=100,
        end_char=178,
        text="Revenue was 1200 million USD and gross profit was 720 million USD in FY2025.",
        **provenance(
            "https://example.com/mock/sec/excs/2025-10-k#page=42",
            fiscal_period="FY2025",
            payload="evidence-chunk-revenue",
        ),
    )
    revenue_fact = FinancialFact(
        id="demo-fact-revenue",
        company_id=company.id,
        security_id=security.id,
        filing_id=filing.id,
        source_document_id=source_document.id,
        evidence_chunk_id=chunk.id,
        metric_name="revenue",
        statement="income_statement",
        value=Decimal("1200.000000"),
        unit="USD_millions",
        scale=Decimal("1000000.000000"),
        formula=None,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 12, 31),
        as_reported=True,
        **provenance(
            "https://example.com/mock/sec/excs/2025-10-k#revenue",
            fiscal_period="FY2025",
            payload="financial-fact-revenue",
        ),
    )
    gross_profit_fact = FinancialFact(
        id="demo-fact-gross-profit",
        company_id=company.id,
        security_id=security.id,
        filing_id=filing.id,
        source_document_id=source_document.id,
        evidence_chunk_id=chunk.id,
        metric_name="gross_profit",
        statement="income_statement",
        value=Decimal("720.000000"),
        unit="USD_millions",
        scale=Decimal("1000000.000000"),
        formula=None,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 12, 31),
        as_reported=True,
        **provenance(
            "https://example.com/mock/sec/excs/2025-10-k#gross-profit",
            fiscal_period="FY2025",
            payload="financial-fact-gross-profit",
        ),
    )
    market_price = MarketPrice(
        id="demo-market-price-excs",
        security_id=security.id,
        price_date=date(2026, 1, 16),
        open_price=Decimal("48.000000"),
        high_price=Decimal("50.000000"),
        low_price=Decimal("47.500000"),
        close_price=Decimal("49.250000"),
        adjusted_close_price=Decimal("49.250000"),
        volume=1_250_000,
        **provenance(
            "https://example.com/mock/prices/excs/2026-01-16",
            fiscal_period=None,
            payload="market-price",
        ),
    )
    macro_series = MacroSeries(
        id="demo-macro-fed-funds",
        series_code="MOCK_FEDFUNDS",
        series_name="Mock Federal Funds Effective Rate",
        observation_date=date(2026, 1, 1),
        value=Decimal("4.250000"),
        unit="percent",
        frequency="monthly",
        seasonal_adjustment="not_seasonally_adjusted",
        **provenance(
            "https://example.com/mock/macro/fedfunds/2026-01",
            currency=None,
            fiscal_period=None,
            payload="macro-series",
        ),
    )
    industry = IndustryTaxonomy(
        id="demo-industry-software",
        taxonomy_name="InsightOS Demo Taxonomy",
        industry_code="TECH-SOFTWARE",
        industry_name="Infrastructure Software",
        level=2,
        description="Mock taxonomy node for infrastructure software companies.",
        **provenance(
            "https://example.com/mock/industry-taxonomy/software",
            currency=None,
            fiscal_period=None,
            payload="industry-taxonomy",
        ),
    )
    industry_mapping = CompanyIndustryMapping(
        id="demo-company-industry-mapping",
        company_id=company.id,
        industry_id=industry.id,
        classification_type="primary",
        valid_from=date(2025, 1, 1),
        valid_to=None,
        **provenance(
            "https://example.com/mock/company-industry/excs",
            currency=None,
            fiscal_period="FY2025",
            payload="company-industry-mapping",
        ),
    )
    report = ResearchReport(
        id="demo-report-excs",
        company_id=company.id,
        title="Example Cloud FY2025 Evidence-Backed Research Note",
        report_type="company_analysis",
        generated_at=datetime(2026, 6, 23, 1, 10, tzinfo=UTC),
        model_version="insightos-demo-model-0.1",
        methodology="Mock report generated from seeded filings, facts, and evidence chunks only.",
        input_snapshot_hash=hash_source("demo-report-inputs"),
        report_status="draft",
        summary="Mock report demonstrating traceable claims.",
        **provenance(
            "internal://insightos/demo/reports/excs",
            fiscal_period="FY2025",
            payload="research-report",
        ),
    )
    valuation = ValuationModel(
        id="demo-valuation-excs",
        company_id=company.id,
        research_report_id=report.id,
        model_type="ev_revenue_multiple",
        scenario="base",
        valuation_date=date(2026, 6, 23),
        base_currency="USD",
        output_metric="enterprise_value_usd_millions",
        output_value=Decimal("6000.000000"),
        formula="revenue * selected_ev_revenue_multiple",
        input_snapshot_hash=hash_source("revenue", "multiple"),
        model_payload={"revenue": "1200.000000", "selected_ev_revenue_multiple": "5.000000"},
        **provenance(
            "internal://insightos/demo/valuation/excs",
            fiscal_period="FY2025",
            payload="valuation-model",
        ),
    )
    assumption = Assumption(
        id="demo-assumption-multiple",
        company_id=company.id,
        research_report_id=report.id,
        valuation_model_id=valuation.id,
        assumption_name="selected_ev_revenue_multiple",
        scenario="base",
        numeric_value=Decimal("5.000000"),
        text_value=None,
        unit="x",
        formula=None,
        rationale="Mock multiple selected only to test valuation traceability.",
        **provenance(
            "internal://insightos/demo/assumptions/excs",
            fiscal_period="FY2025",
            payload="assumption-multiple",
        ),
    )
    claim = ReportClaim(
        id="demo-claim-gross-margin",
        research_report_id=report.id,
        evidence_chunk_id=chunk.id,
        financial_fact_id=gross_profit_fact.id,
        claim_text="Example Cloud reported FY2025 gross profit of 720 million USD.",
        claim_type="financial_summary",
        conclusion_level="fact",
        formula="gross_profit / revenue = 720 / 1200 = 60%",
        generated_at=datetime(2026, 6, 23, 1, 11, tzinfo=UTC),
        evidence_summary="The claim links to the FY2025 10-K evidence chunk and financial fact.",
        **provenance(
            "internal://insightos/demo/report-claims/excs/gross-margin",
            fiscal_period="FY2025",
            payload="report-claim-gross-margin",
        ),
    )
    watchlist = Watchlist(
        id="demo-watchlist",
        name="Demo US Software Coverage",
        owner_label="demo-user",
        description="Mock watchlist for local tests.",
        visibility="private",
        criteria={"ticker": "EXCS", "industry": "Infrastructure Software"},
        **provenance(
            "internal://insightos/demo/watchlists/software",
            fiscal_period=None,
            payload="watchlist",
        ),
    )
    alert = Alert(
        id="demo-alert-price",
        watchlist_id=watchlist.id,
        company_id=company.id,
        security_id=security.id,
        alert_type="price_threshold",
        condition="close_price > 50",
        threshold_value=Decimal("50.000000"),
        unit="USD",
        is_active=True,
        triggered_at=None,
        last_evaluated_at=datetime(2026, 6, 23, 1, 15, tzinfo=UTC),
        **provenance(
            "internal://insightos/demo/alerts/excs-price",
            fiscal_period=None,
            payload="alert-price",
        ),
    )

    session.add_all(
        [
            company,
            security,
            source_document,
            filing,
            chunk,
            revenue_fact,
            gross_profit_fact,
            market_price,
            macro_series,
            industry,
            industry_mapping,
            report,
            valuation,
            assumption,
            claim,
            watchlist,
            alert,
        ]
    )
    session.commit()

    return {
        "company_id": company.id,
        "security_id": security.id,
        "source_document_id": source_document.id,
        "evidence_chunk_id": chunk.id,
        "financial_fact_id": gross_profit_fact.id,
        "research_report_id": report.id,
        "report_claim_id": claim.id,
        "valuation_model_id": valuation.id,
    }
