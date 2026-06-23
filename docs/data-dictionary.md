# InsightOS Data Dictionary

This dictionary defines the MVP research evidence chain. It uses mock/demo records only and does not imply a live market-data integration.

## Required Provenance Fields

Every persisted table carries the same provenance fields:

| Field | Meaning |
| --- | --- |
| `source_name` | Human-readable source label, such as `SEC EDGAR`, `FRED`, or `InsightOS Demo Fixture`. |
| `source_url` | Original or internal source location. Internal user/system data uses an `internal://` URL. |
| `published_at` | Time the source was published or generated. |
| `retrieved_at` | Time InsightOS retrieved or generated the record. |
| `currency` | ISO currency code when monetary data applies. Nullable when not monetary. |
| `fiscal_period` | Fiscal period label such as `FY2025` or `Q1-2026`. Nullable for point-in-time data. |
| `confidence_score` | Decimal from `0` to `1`, representing extraction or generation confidence. |
| `source_hash` | SHA-256 hash of source identity and source payload used for reproducibility. |
| `data_status` | Lifecycle state: `draft`, `active`, `superseded`, `error`, or `deleted`. |

## Core Entity Tables

### `companies`

Canonical company identity. Company-level facts must reference this table.

Key fields: `legal_name`, `display_name`, `cik`, `lei`, `headquarters_country`, `website_url`, `description`.

### `securities`

Tradable security identifiers tied to a company.

Key fields: `company_id`, `ticker`, `exchange`, `security_type`, `primary_listing`, `isin`, `cusip`.

### `industry_taxonomy`

Industry classification tree.

Key fields: `taxonomy_name`, `industry_code`, `industry_name`, `parent_industry_id`, `level`, `description`.

### `company_industry_mapping`

Evidence-backed company-to-industry classification.

Key fields: `company_id`, `industry_id`, `classification_type`, `valid_from`, `valid_to`.

## Source And Evidence Tables

### `source_documents`

Raw or normalized source documents, such as filings, transcripts, company releases, or internal generated artifacts.

Key fields: `company_id`, `document_type`, `title`, `issuer`, `document_date`, `storage_url`, `mime_type`, `raw_text_excerpt`.

### `filings`

SEC-like filing metadata linked to a source document.

Key fields: `company_id`, `source_document_id`, `accession_number`, `filing_type`, `filed_at`, `period_end_date`, `sec_file_number`.

### `evidence_chunks`

Small traceable excerpts from source documents. Report claims should link here whenever a text source supports the claim.

Key fields: `source_document_id`, `chunk_index`, `section_name`, `page_number`, `start_char`, `end_char`, `text`.

## Numeric Data Tables

### `financial_facts`

As-reported or calculated company financial values. Calculated records must include `formula`; as-reported records may leave it null.

Key fields: `company_id`, `security_id`, `filing_id`, `source_document_id`, `evidence_chunk_id`, `metric_name`, `statement`, `value`, `unit`, `scale`, `formula`, `period_start`, `period_end`, `as_reported`.

### `market_prices`

Security-level price observations.

Key fields: `security_id`, `price_date`, `open_price`, `high_price`, `low_price`, `close_price`, `adjusted_close_price`, `volume`.

### `macro_series`

US macroeconomic observations in MVP scope.

Key fields: `series_code`, `series_name`, `observation_date`, `value`, `unit`, `frequency`, `seasonal_adjustment`.

## Research Output Tables

### `research_reports`

Generated report metadata. A report is not a source of truth; it is a generated artifact with an input snapshot hash.

Key fields: `company_id`, `title`, `report_type`, `generated_at`, `model_version`, `methodology`, `input_snapshot_hash`, `report_status`, `summary`.

### `report_claims`

Atomic statements inside a report. Each claim should reference an `evidence_chunk_id`, a `financial_fact_id`, or both.

Key fields: `research_report_id`, `evidence_chunk_id`, `financial_fact_id`, `claim_text`, `claim_type`, `conclusion_level`, `formula`, `generated_at`, `evidence_summary`.

Trace path:

`research_reports -> report_claims -> financial_facts -> filings/source_documents -> evidence_chunks`

This path lets a user verify the generated claim, original number, original text source, formula, confidence score, and generation time.

### `assumptions`

Explicit user/system assumptions used by reports or valuation models.

Key fields: `company_id`, `research_report_id`, `valuation_model_id`, `assumption_name`, `scenario`, `numeric_value`, `text_value`, `unit`, `formula`, `rationale`.

### `valuation_models`

Traceable valuation outputs. The output is an analytical calculation, not investment advice.

Key fields: `company_id`, `research_report_id`, `model_type`, `scenario`, `valuation_date`, `base_currency`, `output_metric`, `output_value`, `formula`, `input_snapshot_hash`, `model_payload`.

## Monitoring Tables

### `watchlists`

Named collections or saved criteria. User-generated data uses `internal://` provenance.

Key fields: `name`, `owner_label`, `description`, `visibility`, `criteria`.

### `alerts`

Saved monitoring rules. Alerts do not imply trade recommendations.

Key fields: `watchlist_id`, `company_id`, `security_id`, `alert_type`, `condition`, `threshold_value`, `unit`, `is_active`, `triggered_at`, `last_evaluated_at`.

## Design Rules

- AI output is never a primary source.
- Every claim must be traceable to source metadata and, where numeric, a source number or formula.
- Calculated facts and valuation outputs must store formulas.
- Demo data must use `InsightOS Demo Fixture` or `internal://` sources, never live market or paid API data.
