from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.demo_data import seed_demo_data
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
from app.schemas import CompanyRead, ReportClaimRead

EVIDENCE_MODELS = [
    Company,
    Security,
    Filing,
    FinancialFact,
    MarketPrice,
    MacroSeries,
    IndustryTaxonomy,
    CompanyIndustryMapping,
    SourceDocument,
    EvidenceChunk,
    ResearchReport,
    ReportClaim,
    Assumption,
    ValuationModel,
    Watchlist,
    Alert,
]

PROVENANCE_COLUMNS = {
    "source_name",
    "source_url",
    "published_at",
    "retrieved_at",
    "currency",
    "fiscal_period",
    "confidence_score",
    "source_hash",
    "data_status",
}


def build_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return session_factory()


def test_all_evidence_models_have_required_provenance_columns() -> None:
    for model in EVIDENCE_MODELS:
        columns = {column.key for column in inspect(model).columns}
        assert PROVENANCE_COLUMNS.issubset(columns), model.__tablename__


def test_demo_data_populates_complete_traceable_evidence_chain() -> None:
    with build_session() as session:
        ids = seed_demo_data(session)

        for model in EVIDENCE_MODELS:
            assert session.scalar(select(model).limit(1)) is not None, model.__tablename__

        claim = session.get(ReportClaim, ids["report_claim_id"])
        assert claim is not None
        assert claim.evidence_chunk is not None
        assert claim.financial_fact is not None
        assert claim.research_report is not None

        assert "gross profit" in claim.claim_text
        assert claim.formula == "gross_profit / revenue = 720 / 1200 = 60%"
        assert "gross profit was 720 million USD" in claim.evidence_chunk.text
        assert claim.financial_fact.value == Decimal("720.000000")
        assert claim.financial_fact.source_document is not None
        assert claim.financial_fact.filing is not None
        assert claim.financial_fact.filing.accession_number == "0000000001-26-000001"
        assert claim.generated_at is not None
        assert claim.source_hash


def test_seeded_rows_have_non_empty_source_metadata() -> None:
    with build_session() as session:
        seed_demo_data(session)

        for model in EVIDENCE_MODELS:
            records = session.scalars(select(model)).all()
            assert records, model.__tablename__
            for record in records:
                assert record.source_name
                assert record.source_url
                assert record.published_at
                assert record.retrieved_at
                assert len(record.source_hash) == 64
                assert Decimal("0") <= record.confidence_score <= Decimal("1")
                assert record.data_status == "active"


def test_pydantic_schemas_validate_from_orm_objects() -> None:
    with build_session() as session:
        ids = seed_demo_data(session)

        company = session.get(Company, ids["company_id"])
        claim = session.get(ReportClaim, ids["report_claim_id"])

        assert company is not None
        assert claim is not None

        company_schema = CompanyRead.model_validate(company)
        claim_schema = ReportClaimRead.model_validate(claim)

        assert company_schema.display_name == "Example Cloud"
        assert claim_schema.financial_fact_id == ids["financial_fact_id"]
        assert claim_schema.confidence_score == Decimal("0.9500")
