from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.connectors.base import SourceMetadata
from app.connectors.market_prices import MarketPriceResponse, PriceBar
from app.connectors.sec import SecConnector
from app.main import app
from app.services.company_research import run_single_company_research

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def sec_mock_client() -> httpx.Client:
    profile = load_fixture("sec_company_profile.json")
    facts = load_fixture("sec_company_facts.json")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = facts if "companyfacts" in str(request.url) else profile
        return httpx.Response(
            200,
            json=payload,
            headers={"last-modified": "Tue, 23 Jun 2026 00:00:00 GMT"},
            request=request,
        )

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_single_company_research_builds_traceable_sec_packet() -> None:
    report = run_single_company_research(
        "NVDA",
        connector=SecConnector(client=sec_mock_client()),
        include_market_data=False,
    )

    metrics = {item.metric: item for item in report["financial_quality"]}
    valuation = report["valuation"]

    assert report["ticker"] == "NVDA"
    assert report["company"]["name"] == "Apple Inc."
    assert report["latest_annual_period"] == "FY2025"
    assert metrics["revenue_growth"].status == "ok"
    assert metrics["gross_margin"].status == "ok"
    assert metrics["free_cash_flow_margin"].status == "ok"
    assert valuation["status"] == "completed"
    assert valuation["dcf"]["base"]["status"] == "ok"
    assert report["sources"][0]["source_hash"]
    assert report["research_report"]["facts"]
    assert "No personalized" in report["limitations"][0]


def test_single_company_research_adds_market_validation_when_prices_exist() -> None:
    report = run_single_company_research(
        "NVDA",
        connector=SecConnector(client=sec_mock_client()),
        market_connector=FakeMarketConnector(),
    )

    assert report["market_price"]["status"] == "ok"
    assert report["historical_validation"]["status"] == "ok"
    assert report["historical_validation"]["summary"]["sample_size"] >= 1
    assert report["investor_decision"]["stance"] in {
        "高优先级跟踪",
        "继续跟踪，暂不形成强结论",
        "证据不足",
    }
    assert report["investor_decision"]["not_personalized_advice"]


def test_company_research_route_returns_service_payload(monkeypatch) -> None:
    def fake_research(ticker: str) -> dict[str, object]:
        return {
            "ticker": ticker.upper(),
            "status": "completed",
            "company": {"name": "Apple Inc."},
        }

    monkeypatch.setattr("app.api.company_research.run_single_company_research", fake_research)

    response = TestClient(app).get("/api/research/company/nvda")

    assert response.status_code == 200
    assert response.json()["ticker"] == "NVDA"


class FakeMarketConnector:
    def get_daily_prices(self, ticker: str) -> MarketPriceResponse:
        bars = [
            PriceBar(
                date=date(2025, 10, 31),
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                volume=1000,
            ),
            PriceBar(
                date=date(2026, 1, 30),
                open=Decimal("110"),
                high=Decimal("111"),
                low=Decimal("109"),
                close=Decimal("110"),
                volume=1000,
            ),
            PriceBar(
                date=date(2026, 4, 29),
                open=Decimal("120"),
                high=Decimal("121"),
                low=Decimal("119"),
                close=Decimal("120"),
                volume=1000,
            ),
            PriceBar(
                date=date(2026, 10, 31),
                open=Decimal("130"),
                high=Decimal("131"),
                low=Decimal("129"),
                close=Decimal("130"),
                volume=1000,
            ),
        ]
        retrieved_at = datetime(2026, 6, 28, tzinfo=UTC)
        return MarketPriceResponse(
            ticker=ticker,
            bars=bars,
            metadata=SourceMetadata(
                source_name="Test Market Prices",
                source_url="https://example.test/prices.csv",
                published_at=retrieved_at,
                retrieved_at=retrieved_at,
                confidence_score=0.8,
                source_hash="test-price-hash",
            ),
            response_status=200,
        )
