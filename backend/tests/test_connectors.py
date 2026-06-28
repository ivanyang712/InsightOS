from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from app.connectors import ConnectorError
from app.connectors.base import stable_hash
from app.connectors.fred import FredConnector, normalize_fred_observations
from app.connectors.market_prices import MarketPriceConnector, parse_stooq_csv
from app.connectors.sec import SecConnector, normalize_company_facts, normalize_filings
from app.services.data_ingestion import raw_record_from_response

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def mock_client(payload: dict, status_code: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json=payload,
            headers={"last-modified": "Tue, 23 Jun 2026 00:00:00 GMT"},
            request=request,
        )

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_sec_filing_normalization_builds_primary_document_urls() -> None:
    payload = load_fixture("sec_company_profile.json")

    filings = normalize_filings("320193", payload)

    assert [filing.filing_type for filing in filings] == ["10-K", "10-Q"]
    assert filings[0].accession_number == "0000320193-25-000079"
    assert filings[0].primary_document_url.endswith("/320193/000032019325000079/aapl-20250927.htm")


def test_sec_company_facts_normalization_extracts_key_metrics() -> None:
    payload = load_fixture("sec_company_facts.json")
    connector = SecConnector(client=mock_client(payload))

    response = connector.get_company_facts("320193")
    facts = normalize_company_facts(response)

    metrics = {fact.metric_name: fact for fact in facts}
    assert metrics["revenues"].value == 391035000000
    assert metrics["operating_income"].unit == "USD"
    assert metrics["net_income"].fiscal_period == "FY2025-FY"


def test_fred_requires_api_key_for_live_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.connectors.fred.settings.fred_api_key", None)

    with pytest.raises(ConnectorError):
        FredConnector(client=mock_client({})).get_series_observations("FEDFUNDS")


def test_fred_normalization_skips_missing_values() -> None:
    payload = load_fixture("fred_observations.json")
    connector = FredConnector(client=mock_client(payload))
    response = connector.get_json("https://api.stlouisfed.org/fred/series/observations")

    observations = normalize_fred_observations(
        "FEDFUNDS", response, unit="percent", frequency="monthly"
    )

    assert len(observations) == 1
    assert observations[0].value == 4.25
    assert observations[0].unit == "percent"


def test_raw_record_preserves_payload_and_source_hash() -> None:
    payload = load_fixture("sec_company_profile.json")
    connector = SecConnector(client=mock_client(payload))
    response = connector.get_company_profile("320193")

    raw = raw_record_from_response("sec", response, normalized_status="profile_loaded")

    assert raw.response_payload["name"] == "Apple Inc."
    assert raw.source_hash == stable_hash(payload)
    assert raw.source_url.startswith("https://data.sec.gov/submissions/")


def test_stooq_price_normalization_extracts_daily_bars() -> None:
    content = "\n".join(
        [
            "Date,Open,High,Low,Close,Volume",
            "2025-01-02,100,105,99,104,1200000",
            "2025-01-03,104,108,103,107,1300000",
        ]
    )

    bars = parse_stooq_csv(content)

    assert len(bars) == 2
    assert bars[0].date.isoformat() == "2025-01-02"
    assert bars[1].close == 107


def test_market_price_connector_preserves_source_metadata() -> None:
    content = "\n".join(
        [
            "Date,Open,High,Low,Close,Volume",
            "2025-01-02,100,105,99,104,1200000",
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=content, request=request)

    connector = MarketPriceConnector(client=httpx.Client(transport=httpx.MockTransport(handler)))
    response = connector.get_daily_prices("NVDA")

    assert response.ticker == "NVDA"
    assert response.bars[0].close == 104
    assert response.metadata.source_name == "Stooq Daily Historical Prices"
    assert response.metadata.source_hash
