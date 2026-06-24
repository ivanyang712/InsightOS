from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def metric(name: str, value: str) -> dict[str, str]:
    return {
        "metric": name,
        "value": value,
        "currency": "USD",
        "unit": "USD_millions",
        "fiscal_period": "FY2026",
        "source_hash": f"hash-{name}".ljust(64, "0")[:64],
    }


def test_financial_quality_api_returns_calculation_results() -> None:
    response = client.post(
        "/api/analysis/financial-quality",
        json={
            "current": [
                metric("revenue", "1200"),
                metric("gross_profit", "720"),
            ],
            "previous": [metric("revenue", "1000")],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    by_metric = {item["metric"]: item for item in payload["metrics"]}
    assert by_metric["gross_margin"]["status"] == "ok"
    assert by_metric["gross_margin"]["formula"] == "gross_profit / revenue"
    assert by_metric["operating_margin"]["status"] == "unavailable"


def test_valuation_api_returns_dcf_and_scenarios() -> None:
    dcf = client.post(
        "/api/analysis/valuation/dcf",
        json={
            "free_cash_flows": ["100", "110", "121"],
            "discount_rate": "0.10",
            "terminal_growth_rate": "0.03",
            "net_debt": "50",
        },
    )
    scenarios = client.post(
        "/api/analysis/valuation/scenarios",
        json={
            "base_free_cash_flow": "100",
            "growth_rates": {"bear": "0.02", "base": "0.10", "bull": "0.20"},
            "years": 3,
        },
    )

    assert dcf.status_code == 200
    assert dcf.json()["status"] == "ok"
    assert scenarios.status_code == 200
    assert set(scenarios.json()["scenarios"]) == {"bear", "base", "bull"}


def test_quality_and_agent_api_return_reviewable_outputs() -> None:
    audit = client.post(
        "/api/analysis/quality/ai-output",
        json={
            "text": "buy now",
            "claims_with_citations": [True],
            "calculation_statuses": [],
        },
    )
    report = client.post(
        "/api/analysis/agents/research-report",
        json={
            "evidence": [
                {
                    "id": "e1",
                    "text": "Revenue increased in the fixture.",
                    "citation": {
                        "source_name": "Demo",
                        "source_url": "internal://demo",
                        "published_at": "2026-06-23",
                        "retrieved_at": "2026-06-23T00:00:00Z",
                        "confidence_score": "0.9",
                    },
                }
            ]
        },
    )

    assert audit.status_code == 200
    assert audit.json()["issues"][0]["category"] == "investment_promise_language"
    assert report.status_code == 200
    assert report.json()["facts"] == ["Revenue increased in the fixture."]
