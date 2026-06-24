from __future__ import annotations

from decimal import Decimal

from app.services.financial_analysis import (
    MetricValue,
    bull_base_bear_scenarios,
    calculate_financial_quality_metrics,
    dcf_valuation,
    multiple_valuation,
    reverse_dcf_required_growth,
)


def value(metric: str, amount: str, period: str = "FY2025") -> MetricValue:
    return MetricValue(
        metric=metric,
        value=Decimal(amount),
        currency="USD",
        unit="USD_millions",
        fiscal_period=period,
        source_hash=f"hash-{metric}-{period}",
    )


def test_financial_quality_metrics_are_deterministic() -> None:
    current = {
        "revenue": value("revenue", "1200"),
        "gross_profit": value("gross_profit", "720"),
        "operating_income": value("operating_income", "360"),
        "net_income": value("net_income", "240"),
        "ebitda": value("ebitda", "420"),
        "tax_rate": value("tax_rate", "0.21"),
        "total_debt": value("total_debt", "300"),
        "shareholders_equity": value("shareholders_equity", "900"),
        "cash": value("cash", "200"),
        "free_cash_flow": value("free_cash_flow", "300"),
        "current_assets": value("current_assets", "600"),
        "current_liabilities": value("current_liabilities", "300"),
        "interest_expense": value("interest_expense", "30"),
        "shares_outstanding": value("shares_outstanding", "100"),
        "cost_of_goods_sold": value("cost_of_goods_sold", "480"),
        "average_inventory": value("average_inventory", "120"),
        "average_accounts_receivable": value("average_accounts_receivable", "100"),
        "average_accounts_payable": value("average_accounts_payable", "80"),
    }
    previous = {
        "revenue": value("revenue", "1000", "FY2024"),
        "shares_outstanding": value("shares_outstanding", "98", "FY2024"),
    }

    metrics = {
        result.metric: result for result in calculate_financial_quality_metrics(current, previous)
    }

    assert metrics["revenue_growth"].value == Decimal("0.2")
    assert metrics["gross_margin"].value == Decimal("0.6")
    assert metrics["current_ratio"].value == Decimal("2")
    assert metrics["interest_coverage"].formula == "operating_income / interest_expense"
    assert metrics["cash_conversion_cycle"].status == "ok"


def test_missing_inputs_return_unavailable() -> None:
    metrics = {result.metric: result for result in calculate_financial_quality_metrics({}, None)}

    assert metrics["gross_margin"].status == "unavailable"
    assert metrics["gross_margin"].message is not None
    assert metrics["gross_margin"].message.startswith("无法可靠计算")


def test_dcf_valuation_outputs_formula_and_values() -> None:
    result = dcf_valuation(
        [Decimal("100"), Decimal("110"), Decimal("121")],
        Decimal("0.10"),
        Decimal("0.03"),
        Decimal("50"),
    )

    assert result["status"] == "ok"
    assert result["enterprise_value"] > Decimal("1000")
    assert result["equity_value"] == result["enterprise_value"] - Decimal("50")
    assert "terminal_value" in result["formula"]


def test_dcf_rejects_invalid_terminal_growth() -> None:
    result = dcf_valuation([Decimal("100")], Decimal("0.03"), Decimal("0.03"), Decimal("0"))

    assert result["status"] == "unavailable"


def test_multiple_valuation_and_scenarios() -> None:
    pe = multiple_valuation("pe", Decimal("2000"), Decimal("100"), Decimal("25"))
    scenarios = bull_base_bear_scenarios(
        Decimal("100"),
        {"bear": Decimal("0.02"), "base": Decimal("0.10"), "bull": Decimal("0.20")},
    )

    assert pe["implied_value"] == Decimal("2500")
    assert scenarios["base"][2] == Decimal("133.100")


def test_reverse_dcf_solves_growth_rate() -> None:
    result = reverse_dcf_required_growth(
        Decimal("1500"),
        Decimal("100"),
        Decimal("0.10"),
        Decimal("0.03"),
    )

    assert result["status"] == "ok"
    assert Decimal("-0.50") < result["required_growth_rate"] < Decimal("1.00")
