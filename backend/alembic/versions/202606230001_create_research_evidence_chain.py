"""create research evidence chain

Revision ID: 202606230001
Revises:
Create Date: 2026-06-23 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202606230001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def common_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("fiscal_period", sa.String(length=32), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("source_hash", sa.String(length=64), nullable=False),
        sa.Column("data_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    ]


def upgrade() -> None:
    op.create_table(
        "companies",
        *common_columns(),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("cik", sa.String(length=20), nullable=True),
        sa.Column("lei", sa.String(length=20), nullable=True),
        sa.Column("headquarters_country", sa.String(length=2), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("cik"),
        sa.UniqueConstraint("lei"),
    )

    op.create_table(
        "securities",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=False),
        sa.Column("security_type", sa.String(length=64), nullable=False),
        sa.Column("primary_listing", sa.Boolean(), nullable=False),
        sa.Column("isin", sa.String(length=12), nullable=True),
        sa.Column("cusip", sa.String(length=9), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.UniqueConstraint("ticker", "exchange", name="uq_securities_ticker_exchange"),
    )

    op.create_table(
        "source_documents",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("issuer", sa.String(length=255), nullable=True),
        sa.Column("document_date", sa.Date(), nullable=True),
        sa.Column("storage_url", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("raw_text_excerpt", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )

    op.create_table(
        "filings",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column("accession_number", sa.String(length=64), nullable=False),
        sa.Column("filing_type", sa.String(length=32), nullable=False),
        sa.Column("filed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end_date", sa.Date(), nullable=True),
        sa.Column("sec_file_number", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["source_document_id"], ["source_documents.id"]),
        sa.UniqueConstraint("accession_number", name="uq_filings_accession_number"),
    )

    op.create_table(
        "evidence_chunks",
        *common_columns(),
        sa.Column("source_document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("section_name", sa.String(length=255), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("start_char", sa.Integer(), nullable=True),
        sa.Column("end_char", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["source_document_id"], ["source_documents.id"]),
        sa.UniqueConstraint("source_document_id", "chunk_index", name="uq_chunks_document_index"),
    )

    op.create_table(
        "financial_facts",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("security_id", sa.String(length=36), nullable=True),
        sa.Column("filing_id", sa.String(length=36), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), nullable=True),
        sa.Column("evidence_chunk_id", sa.String(length=36), nullable=True),
        sa.Column("metric_name", sa.String(length=120), nullable=False),
        sa.Column("statement", sa.String(length=64), nullable=True),
        sa.Column("value", sa.Numeric(24, 6), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("scale", sa.Numeric(24, 6), nullable=True),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("as_reported", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["security_id"], ["securities.id"]),
        sa.ForeignKeyConstraint(["filing_id"], ["filings.id"]),
        sa.ForeignKeyConstraint(["source_document_id"], ["source_documents.id"]),
        sa.ForeignKeyConstraint(["evidence_chunk_id"], ["evidence_chunks.id"]),
        sa.UniqueConstraint(
            "company_id",
            "metric_name",
            "fiscal_period",
            "source_hash",
            name="uq_financial_facts_metric_period_source",
        ),
    )

    op.create_table(
        "market_prices",
        *common_columns(),
        sa.Column("security_id", sa.String(length=36), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open_price", sa.Numeric(24, 6), nullable=True),
        sa.Column("high_price", sa.Numeric(24, 6), nullable=True),
        sa.Column("low_price", sa.Numeric(24, 6), nullable=True),
        sa.Column("close_price", sa.Numeric(24, 6), nullable=False),
        sa.Column("adjusted_close_price", sa.Numeric(24, 6), nullable=True),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["security_id"], ["securities.id"]),
        sa.UniqueConstraint(
            "security_id", "price_date", "source_hash", name="uq_prices_security_date_source"
        ),
    )

    op.create_table(
        "macro_series",
        *common_columns(),
        sa.Column("series_code", sa.String(length=64), nullable=False),
        sa.Column("series_name", sa.String(length=255), nullable=False),
        sa.Column("observation_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(24, 6), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.Column("frequency", sa.String(length=32), nullable=False),
        sa.Column("seasonal_adjustment", sa.String(length=64), nullable=True),
        sa.UniqueConstraint(
            "series_code",
            "observation_date",
            "source_hash",
            name="uq_macro_series_observation_source",
        ),
    )

    op.create_table(
        "industry_taxonomy",
        *common_columns(),
        sa.Column("taxonomy_name", sa.String(length=64), nullable=False),
        sa.Column("industry_code", sa.String(length=64), nullable=False),
        sa.Column("industry_name", sa.String(length=255), nullable=False),
        sa.Column("parent_industry_id", sa.String(length=36), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["parent_industry_id"], ["industry_taxonomy.id"]),
        sa.UniqueConstraint("taxonomy_name", "industry_code", name="uq_industry_taxonomy_code"),
    )

    op.create_table(
        "company_industry_mapping",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("industry_id", sa.String(length=36), nullable=False),
        sa.Column("classification_type", sa.String(length=64), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["industry_id"], ["industry_taxonomy.id"]),
        sa.UniqueConstraint(
            "company_id",
            "industry_id",
            "classification_type",
            name="uq_company_industry_classification",
        ),
    )

    op.create_table(
        "research_reports",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("report_type", sa.String(length=64), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("methodology", sa.Text(), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("report_status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
    )

    op.create_table(
        "valuation_models",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("research_report_id", sa.String(length=36), nullable=True),
        sa.Column("model_type", sa.String(length=64), nullable=False),
        sa.Column("scenario", sa.String(length=64), nullable=False),
        sa.Column("valuation_date", sa.Date(), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("output_metric", sa.String(length=120), nullable=False),
        sa.Column("output_value", sa.Numeric(24, 6), nullable=False),
        sa.Column("formula", sa.Text(), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("model_payload", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["research_report_id"], ["research_reports.id"]),
    )

    op.create_table(
        "assumptions",
        *common_columns(),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("research_report_id", sa.String(length=36), nullable=True),
        sa.Column("valuation_model_id", sa.String(length=36), nullable=True),
        sa.Column("assumption_name", sa.String(length=120), nullable=False),
        sa.Column("scenario", sa.String(length=64), nullable=False),
        sa.Column("numeric_value", sa.Numeric(24, 6), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=True),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["research_report_id"], ["research_reports.id"]),
        sa.ForeignKeyConstraint(["valuation_model_id"], ["valuation_models.id"]),
    )

    op.create_table(
        "report_claims",
        *common_columns(),
        sa.Column("research_report_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_chunk_id", sa.String(length=36), nullable=True),
        sa.Column("financial_fact_id", sa.String(length=36), nullable=True),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("claim_type", sa.String(length=64), nullable=False),
        sa.Column("conclusion_level", sa.String(length=64), nullable=False),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["research_report_id"], ["research_reports.id"]),
        sa.ForeignKeyConstraint(["evidence_chunk_id"], ["evidence_chunks.id"]),
        sa.ForeignKeyConstraint(["financial_fact_id"], ["financial_facts.id"]),
    )

    op.create_table(
        "watchlists",
        *common_columns(),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("owner_label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("visibility", sa.String(length=32), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=True),
    )

    op.create_table(
        "alerts",
        *common_columns(),
        sa.Column("watchlist_id", sa.String(length=36), nullable=True),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("security_id", sa.String(length=36), nullable=True),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("condition", sa.Text(), nullable=False),
        sa.Column("threshold_value", sa.Numeric(24, 6), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["watchlist_id"], ["watchlists.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["security_id"], ["securities.id"]),
    )


def downgrade() -> None:
    for table_name in (
        "alerts",
        "watchlists",
        "report_claims",
        "assumptions",
        "valuation_models",
        "research_reports",
        "company_industry_mapping",
        "industry_taxonomy",
        "macro_series",
        "market_prices",
        "financial_facts",
        "evidence_chunks",
        "filings",
        "source_documents",
        "securities",
        "companies",
    ):
        op.drop_table(table_name)
