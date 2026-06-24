from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx

from app.connectors.base import ConnectorResponse, HttpConnector
from app.core.config import settings

SEC_DATA_BASE = "https://data.sec.gov"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


@dataclass(frozen=True)
class NormalizedFiling:
    accession_number: str
    filing_type: str
    filed_at: str
    period_end_date: str | None
    primary_document_url: str


@dataclass(frozen=True)
class NormalizedFinancialFact:
    metric_name: str
    value: Decimal
    unit: str
    fiscal_period: str
    fiscal_year: int | None
    filed_at: str | None
    source_url: str
    source_hash: str


class SecConnector(HttpConnector):
    source_name = "SEC EDGAR"

    def __init__(self, client: httpx.Client | None = None) -> None:
        super().__init__(
            timeout_seconds=settings.connector_timeout_seconds,
            cache_ttl_seconds=settings.connector_cache_ttl_seconds,
            max_requests_per_second=10,
            client=client,
            headers={
                "User-Agent": settings.sec_user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "data.sec.gov",
            },
        )

    def get_company_profile(self, cik: str) -> ConnectorResponse:
        return self.get_json(f"{SEC_DATA_BASE}/submissions/CIK{normalize_cik(cik)}.json")

    def get_filing_list(self, cik: str) -> list[NormalizedFiling]:
        response = self.get_company_profile(cik)
        return normalize_filings(cik, response.payload)

    def get_company_facts(self, cik: str) -> ConnectorResponse:
        return self.get_json(f"{SEC_DATA_BASE}/api/xbrl/companyfacts/CIK{normalize_cik(cik)}.json")

    def get_key_financial_facts(self, cik: str) -> list[NormalizedFinancialFact]:
        response = self.get_company_facts(cik)
        return normalize_company_facts(response)


def normalize_cik(cik: str) -> str:
    digits = "".join(character for character in cik if character.isdigit())
    return digits.zfill(10)


def normalize_filings(cik: str, payload: dict[str, Any]) -> list[NormalizedFiling]:
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    documents = recent.get("primaryDocument", [])
    normalized: list[NormalizedFiling] = []
    cik_int = str(int(normalize_cik(cik)))

    for index, form in enumerate(forms):
        if form not in {"10-K", "10-Q", "8-K"}:
            continue
        accession = accessions[index]
        accession_compact = accession.replace("-", "")
        primary_document = documents[index]
        normalized.append(
            NormalizedFiling(
                accession_number=accession,
                filing_type=form,
                filed_at=filing_dates[index],
                period_end_date=report_dates[index] or None,
                primary_document_url=(
                    f"{SEC_ARCHIVES_BASE}/{cik_int}/{accession_compact}/{primary_document}"
                ),
            )
        )
    return normalized


SEC_TAG_MAP = {
    "revenues": ["Revenues", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "debt": ["DebtCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditure": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "shares_outstanding": ["EntityCommonStockSharesOutstanding"],
}


def normalize_company_facts(response: ConnectorResponse) -> list[NormalizedFinancialFact]:
    us_gaap = response.payload.get("facts", {}).get("us-gaap", {})
    normalized: list[NormalizedFinancialFact] = []

    for metric_name, candidate_tags in SEC_TAG_MAP.items():
        for tag in candidate_tags:
            concept = us_gaap.get(tag)
            if concept is None:
                continue
            for unit, observations in concept.get("units", {}).items():
                for observation in observations:
                    value = observation.get("val")
                    fiscal_year = observation.get("fy")
                    fiscal_period = observation.get("fp")
                    if value is None or fiscal_period is None:
                        continue
                    normalized.append(
                        NormalizedFinancialFact(
                            metric_name=metric_name,
                            value=Decimal(str(value)),
                            unit=unit,
                            fiscal_period=f"FY{fiscal_year}-{fiscal_period}",
                            fiscal_year=int(fiscal_year) if fiscal_year is not None else None,
                            filed_at=observation.get("filed"),
                            source_url=response.metadata.source_url,
                            source_hash=response.metadata.source_hash,
                        )
                    )
            break
    return normalized
