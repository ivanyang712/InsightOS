from __future__ import annotations

import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

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


def test_single_company_research_builds_traceable_aapl_packet() -> None:
    report = run_single_company_research("AAPL", connector=SecConnector(client=sec_mock_client()))

    metrics = {item.metric: item for item in report["financial_quality"]}
    valuation = report["valuation"]

    assert report["ticker"] == "AAPL"
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


def test_company_research_route_returns_service_payload(monkeypatch) -> None:
    def fake_research(ticker: str) -> dict[str, object]:
        return {
            "ticker": ticker.upper(),
            "status": "completed",
            "company": {"name": "Apple Inc."},
        }

    monkeypatch.setattr("app.api.company_research.run_single_company_research", fake_research)

    response = TestClient(app).get("/api/research/company/aapl")

    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
