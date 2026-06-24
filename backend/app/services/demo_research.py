from __future__ import annotations

from decimal import Decimal

from app.services.agents import Citation, EvidenceItem, orchestrate_research_report
from app.services.archetypes import match_company_archetype
from app.services.financial_analysis import (
    MetricValue,
    bull_base_bear_scenarios,
    calculate_financial_quality_metrics,
    dcf_valuation,
    multiple_valuation,
)
from app.services.quality import audit_ai_output, check_data_quality

DEMO_NOTICE = (
    "Synthetic demo data for workflow testing only. Not production market data and not "
    "investment advice."
)


def demo_metric(metric: str, value: str, period: str = "FY2026") -> MetricValue:
    return MetricValue(
        metric=metric,
        value=Decimal(value),
        currency="USD",
        unit="USD_millions",
        fiscal_period=period,
        source_hash=f"demo-{metric}-{period}",
    )


def nvidia_demo_report() -> dict[str, object]:
    current = {
        "revenue": demo_metric("revenue", "120000"),
        "gross_profit": demo_metric("gross_profit", "90000"),
        "operating_income": demo_metric("operating_income", "72000"),
        "net_income": demo_metric("net_income", "60000"),
        "ebitda": demo_metric("ebitda", "76000"),
        "tax_rate": demo_metric("tax_rate", "0.14"),
        "total_debt": demo_metric("total_debt", "10000"),
        "shareholders_equity": demo_metric("shareholders_equity", "80000"),
        "cash": demo_metric("cash", "50000"),
        "free_cash_flow": demo_metric("free_cash_flow", "58000"),
        "current_assets": demo_metric("current_assets", "90000"),
        "current_liabilities": demo_metric("current_liabilities", "30000"),
        "interest_expense": demo_metric("interest_expense", "300"),
        "shares_outstanding": demo_metric("shares_outstanding", "24500", "FY2026"),
    }
    previous = {
        "revenue": demo_metric("revenue", "85000", "FY2025"),
        "shares_outstanding": demo_metric("shares_outstanding", "24700", "FY2025"),
    }
    calculations = calculate_financial_quality_metrics(current, previous)
    scenarios = bull_base_bear_scenarios(
        Decimal("58000"),
        {"bear": Decimal("0.05"), "base": Decimal("0.16"), "bull": Decimal("0.26")},
    )
    dcf = {
        scenario: dcf_valuation(cash_flows, Decimal("0.10"), Decimal("0.035"), Decimal("-40000"))
        for scenario, cash_flows in scenarios.items()
    }
    valuation = {
        "dcf": dcf,
        "ev_sales": multiple_valuation(
            "ev_sales", Decimal("2500000"), current["revenue"].value, Decimal("18")
        ),
        "pe": multiple_valuation(
            "pe", Decimal("2500000"), current["net_income"].value, Decimal("35")
        ),
    }
    citation = Citation(
        source_name="InsightOS Synthetic Nvidia Fixture",
        source_url="internal://insightos/demo/nvidia",
        published_at="2026-06-23",
        retrieved_at="2026-06-23T00:00:00Z",
        confidence_score=Decimal("0.9000"),
    )
    evidence = [
        EvidenceItem(
            id="nvda-demand",
            text=(
                "Demo fixture indicates AI accelerator demand remains strong but depends "
                "on hyperscaler capex."
            ),
            citation=citation,
        ),
        EvidenceItem(
            id="nvda-dc-quality",
            text="Demo fixture separates data center revenue quality from one-time inventory fill.",
            citation=citation,
        ),
        EvidenceItem(
            id="nvda-margin",
            text=(
                "Demo fixture flags gross margin sensitivity to mix, supply constraints, "
                "and competition."
            ),
            citation=citation,
            fact_value=str(current["gross_profit"].value),
            formula="gross_profit / revenue",
        ),
    ]
    agent_report = orchestrate_research_report(evidence)
    quality_issues = check_data_quality(list(current.values())) + audit_ai_output(
        "No buy/sell language. Demo only.",
        [True, True, True],
        calculations,
    )
    return {
        "demo_notice": DEMO_NOTICE,
        "company": {
            "name": "Nvidia",
            "ticker": "NVDA",
            "archetype": match_company_archetype("NVDA"),
        },
        "research_output": {
            "executive_summary": (
                "Demo workflow: demand durability depends on AI capex breadth, margin "
                "mix, and customer concentration evidence."
            ),
            "business_model": (
                "Demo fixture: accelerated computing platform with hardware, networking, "
                "and software ecosystem exposure."
            ),
            "industry_competitive_position": (
                "Demo fixture: semiconductor archetype emphasizes cycle, export "
                "controls, customer concentration, and gross margin."
            ),
            "financial_quality": calculations,
            "valuation": valuation,
            "risks": [
                "AI capex digestion risk",
                "gross margin normalization risk",
                "hyperscaler customer concentration risk",
                "export-control and supply-chain risk",
            ],
            "catalysts": [
                "new platform cycle",
                "broader enterprise inference adoption",
                "supply expansion",
            ],
            "bull_base_bear": scenarios,
            "key_assumptions": {
                "bear_growth": "5% FCF CAGR for three demo years",
                "base_growth": "16% FCF CAGR for three demo years",
                "bull_growth": "26% FCF CAGR for three demo years",
            },
            "sources_and_confidence": agent_report["citations"],
        },
        "agent_report": agent_report,
        "quality_issues": quality_issues,
    }


def semiconductor_equipment_demo() -> dict[str, object]:
    citation = {
        "source_name": "InsightOS Synthetic Semiconductor Equipment Fixture",
        "source_url": "internal://insightos/demo/semiconductor-equipment",
        "published_at": "2026-06-23",
        "retrieved_at": "2026-06-23T00:00:00Z",
        "confidence_level": "demo-high",
    }
    return {
        "demo_notice": DEMO_NOTICE,
        "industry": "Global Semiconductor Equipment",
        "value_chain_map": {
            "upstream": ["precision components", "optics", "vacuum systems", "specialty materials"],
            "midstream": ["lithography", "etch", "deposition", "metrology", "inspection"],
            "downstream": ["foundries", "memory makers", "IDMs", "advanced packaging"],
        },
        "market_size_growth_drivers": [
            "advanced-node capex",
            "AI accelerator demand",
            "memory technology transitions",
            "regional fab localization",
        ],
        "competitive_landscape": [
            "high technical barriers",
            "installed-base service revenue",
            "export-control segmentation",
        ],
        "cycle_indicators": [
            "book-to-bill",
            "wafer fab equipment spend",
            "memory pricing",
            "foundry utilization",
        ],
        "regional_differences": {
            "US": "process control, deposition, etch, and design ecosystem strength",
            "Japan": "materials, metrology, and specialty equipment depth",
            "Korea": "memory manufacturing demand center",
            "China": "localization push with export-control constraints",
        },
        "three_year_risks_catalysts": {
            "risks": ["capex digestion", "export restrictions", "memory downturn"],
            "catalysts": ["advanced packaging", "HBM demand", "fab localization subsidies"],
        },
        "tracking_metrics": [
            "book-to-bill",
            "lead times",
            "foundry utilization",
            "memory ASP",
            "capex guidance",
        ],
        "sources": [citation],
    }


def cloud_platform_comparison_demo() -> dict[str, object]:
    companies = {
        "MSFT": {
            "cloud_growth": 82,
            "ai_capex": 70,
            "fcf": 86,
            "valuation": 60,
            "moat": 88,
            "regulatory_risk": 55,
        },
        "GOOGL": {
            "cloud_growth": 75,
            "ai_capex": 76,
            "fcf": 90,
            "valuation": 68,
            "moat": 86,
            "regulatory_risk": 70,
        },
        "AMZN": {
            "cloud_growth": 78,
            "ai_capex": 82,
            "fcf": 74,
            "valuation": 62,
            "moat": 84,
            "regulatory_risk": 58,
        },
    }
    rows = []
    for ticker, scores in companies.items():
        rows.append(
            {
                "ticker": ticker,
                "scores": scores,
                "three_year_growth_assumption": (
                    "Synthetic demo assumption only; replace with sourced model inputs."
                ),
            }
        )
    return {
        "demo_notice": DEMO_NOTICE,
        "comparison": "Microsoft vs Google vs Amazon",
        "score_matrix": rows,
        "sources": [
            {
                "source_name": "InsightOS Synthetic Cloud Comparison Fixture",
                "source_url": "internal://insightos/demo/cloud-comparison",
                "published_at": "2026-06-23",
                "retrieved_at": "2026-06-23T00:00:00Z",
                "confidence_level": "demo-high",
            }
        ],
    }
