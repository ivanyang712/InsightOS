from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Any


@dataclass(frozen=True)
class MetricValue:
    metric: str
    value: Decimal
    currency: str | None
    unit: str
    fiscal_period: str
    source_hash: str


@dataclass(frozen=True)
class CalculationResult:
    metric: str
    status: str
    value: Decimal | None
    unit: str
    fiscal_period: str
    formula: str
    inputs: dict[str, MetricValue]
    calculated_at: datetime
    message: str | None = None


def calculate_financial_quality_metrics(
    current: dict[str, MetricValue],
    previous: dict[str, MetricValue] | None = None,
) -> list[CalculationResult]:
    return [
        revenue_growth(current, previous),
        ratio("gross_margin", current, "gross_profit", "revenue", "gross_profit / revenue"),
        ratio(
            "operating_margin", current, "operating_income", "revenue", "operating_income / revenue"
        ),
        ratio("net_margin", current, "net_income", "revenue", "net_income / revenue"),
        ratio("ebitda_margin", current, "ebitda", "revenue", "ebitda / revenue"),
        roic(current),
        ratio(
            "roe", current, "net_income", "shareholders_equity", "net_income / shareholders_equity"
        ),
        ratio(
            "free_cash_flow_margin",
            current,
            "free_cash_flow",
            "revenue",
            "free_cash_flow / revenue",
        ),
        ratio("debt_to_ebitda", current, "total_debt", "ebitda", "total_debt / ebitda"),
        net_debt_to_ebitda(current),
        ratio(
            "current_ratio",
            current,
            "current_assets",
            "current_liabilities",
            "current_assets / current_liabilities",
        ),
        ratio(
            "interest_coverage",
            current,
            "operating_income",
            "interest_expense",
            "operating_income / interest_expense",
        ),
        share_dilution(current, previous),
        ratio(
            "inventory_turnover",
            current,
            "cost_of_goods_sold",
            "average_inventory",
            "cogs / average_inventory",
        ),
        receivable_days(current),
        cash_conversion_cycle(current),
    ]


def ratio(
    metric: str,
    values: dict[str, MetricValue],
    numerator_key: str,
    denominator_key: str,
    formula: str,
    *,
    unit: str = "ratio",
) -> CalculationResult:
    inputs = require_inputs(values, numerator_key, denominator_key)
    if len(inputs) < 2:
        return unavailable(
            metric, values, formula, f"Missing {numerator_key} or {denominator_key}."
        )
    numerator = inputs[numerator_key]
    denominator = inputs[denominator_key]
    return divide(metric, numerator, denominator, formula, unit=unit, inputs=inputs)


def revenue_growth(
    current: dict[str, MetricValue], previous: dict[str, MetricValue] | None
) -> CalculationResult:
    formula = "(current_revenue - previous_revenue) / previous_revenue"
    if previous is None:
        return unavailable("revenue_growth", current, formula, "Missing previous period revenue.")
    inputs = require_inputs(current, "revenue") | {
        f"previous_{key}": value for key, value in require_inputs(previous, "revenue").items()
    }
    if "revenue" not in inputs or "previous_revenue" not in inputs:
        return unavailable(
            "revenue_growth", current, formula, "Missing current or previous revenue."
        )
    current_revenue = inputs["revenue"]
    previous_revenue = inputs["previous_revenue"]
    numerator = MetricValue(
        metric="revenue_delta",
        value=current_revenue.value - previous_revenue.value,
        currency=current_revenue.currency,
        unit=current_revenue.unit,
        fiscal_period=current_revenue.fiscal_period,
        source_hash=f"{current_revenue.source_hash}:{previous_revenue.source_hash}",
    )
    return divide(
        "revenue_growth",
        numerator,
        previous_revenue,
        formula,
        unit="percent",
        inputs=inputs,
    )


def roic(values: dict[str, MetricValue]) -> CalculationResult:
    formula = "operating_income * (1 - tax_rate) / (total_debt + shareholders_equity - cash)"
    inputs = require_inputs(
        values, "operating_income", "tax_rate", "total_debt", "shareholders_equity", "cash"
    )
    if len(inputs) < 5:
        return unavailable(
            "roic", values, formula, "Missing operating income, tax rate, debt, equity, or cash."
        )
    nopat = inputs["operating_income"].value * (Decimal("1") - inputs["tax_rate"].value)
    invested_capital = (
        inputs["total_debt"].value + inputs["shareholders_equity"].value - inputs["cash"].value
    )
    denominator = MetricValue(
        metric="invested_capital",
        value=invested_capital,
        currency=inputs["total_debt"].currency,
        unit=inputs["total_debt"].unit,
        fiscal_period=inputs["total_debt"].fiscal_period,
        source_hash=":".join(value.source_hash for value in inputs.values()),
    )
    numerator = MetricValue(
        metric="nopat",
        value=nopat,
        currency=inputs["operating_income"].currency,
        unit=inputs["operating_income"].unit,
        fiscal_period=inputs["operating_income"].fiscal_period,
        source_hash=denominator.source_hash,
    )
    return divide("roic", numerator, denominator, formula, unit="percent", inputs=inputs)


def net_debt_to_ebitda(values: dict[str, MetricValue]) -> CalculationResult:
    formula = "(total_debt - cash) / ebitda"
    inputs = require_inputs(values, "total_debt", "cash", "ebitda")
    if len(inputs) < 3:
        return unavailable("net_debt_to_ebitda", values, formula, "Missing debt, cash, or EBITDA.")
    net_debt = MetricValue(
        metric="net_debt",
        value=inputs["total_debt"].value - inputs["cash"].value,
        currency=inputs["total_debt"].currency,
        unit=inputs["total_debt"].unit,
        fiscal_period=inputs["total_debt"].fiscal_period,
        source_hash=f"{inputs['total_debt'].source_hash}:{inputs['cash'].source_hash}",
    )
    return divide(
        "net_debt_to_ebitda", net_debt, inputs["ebitda"], formula, unit="ratio", inputs=inputs
    )


def share_dilution(
    current: dict[str, MetricValue], previous: dict[str, MetricValue] | None
) -> CalculationResult:
    formula = "(current_shares - previous_shares) / previous_shares"
    if previous is None:
        return unavailable("share_dilution", current, formula, "Missing previous period shares.")
    inputs = require_inputs(current, "shares_outstanding") | {
        f"previous_{key}": value
        for key, value in require_inputs(previous, "shares_outstanding").items()
    }
    if "shares_outstanding" not in inputs or "previous_shares_outstanding" not in inputs:
        return unavailable(
            "share_dilution", current, formula, "Missing current or previous shares."
        )
    current_shares = inputs["shares_outstanding"]
    previous_shares = inputs["previous_shares_outstanding"]
    delta = MetricValue(
        metric="share_delta",
        value=current_shares.value - previous_shares.value,
        currency=None,
        unit=current_shares.unit,
        fiscal_period=current_shares.fiscal_period,
        source_hash=f"{current_shares.source_hash}:{previous_shares.source_hash}",
    )
    return divide("share_dilution", delta, previous_shares, formula, unit="percent", inputs=inputs)


def receivable_days(values: dict[str, MetricValue]) -> CalculationResult:
    formula = "average_accounts_receivable / revenue * 365"
    inputs = require_inputs(values, "average_accounts_receivable", "revenue")
    if len(inputs) < 2:
        return unavailable("receivable_days", values, formula, "Missing receivables or revenue.")
    result = divide(
        "receivable_days",
        inputs["average_accounts_receivable"],
        inputs["revenue"],
        formula,
        unit="days",
        inputs=inputs,
    )
    if result.value is None:
        return result
    return replace_value(result, result.value * Decimal("365"))


def cash_conversion_cycle(values: dict[str, MetricValue]) -> CalculationResult:
    formula = "inventory_days + receivable_days - payable_days"
    required = require_inputs(
        values,
        "average_inventory",
        "cost_of_goods_sold",
        "average_accounts_receivable",
        "revenue",
        "average_accounts_payable",
    )
    if len(required) < 5:
        return unavailable(
            "cash_conversion_cycle", values, formula, "Missing working-capital inputs."
        )
    inventory_days_result = divide(
        "inventory_days",
        required["average_inventory"],
        required["cost_of_goods_sold"],
        "average_inventory / cogs * 365",
        unit="days",
        inputs=required,
    )
    if inventory_days_result.value is not None:
        inventory_days_result = replace_value(
            inventory_days_result, inventory_days_result.value * Decimal("365")
        )
    receivable_days_result = receivable_days(values)
    payable_days_result = divide(
        "payable_days",
        required["average_accounts_payable"],
        required["cost_of_goods_sold"],
        "average_accounts_payable / cogs * 365",
        unit="days",
        inputs=required,
    )
    if payable_days_result.value is not None:
        payable_days_result = replace_value(
            payable_days_result, payable_days_result.value * Decimal("365")
        )
    if (
        inventory_days_result.value is None
        or receivable_days_result.value is None
        or payable_days_result.value is None
    ):
        return unavailable(
            "cash_conversion_cycle", values, formula, "Unable to calculate component days."
        )
    value = inventory_days_result.value + receivable_days_result.value - payable_days_result.value
    return CalculationResult(
        metric="cash_conversion_cycle",
        status="ok",
        value=value,
        unit="days",
        fiscal_period=next(iter(required.values())).fiscal_period,
        formula=formula,
        inputs=required,
        calculated_at=datetime.now(UTC),
    )


def dcf_valuation(
    free_cash_flows: list[Decimal],
    discount_rate: Decimal,
    terminal_growth_rate: Decimal,
    net_debt: Decimal,
) -> dict[str, Any]:
    if not free_cash_flows:
        return unavailable_payload("dcf", "Missing free cash flow forecast.")
    if discount_rate <= terminal_growth_rate:
        return unavailable_payload("dcf", "Discount rate must exceed terminal growth rate.")
    present_value = Decimal("0")
    for index, cash_flow in enumerate(free_cash_flows, start=1):
        present_value += cash_flow / ((Decimal("1") + discount_rate) ** index)
    terminal_value = (
        free_cash_flows[-1]
        * (Decimal("1") + terminal_growth_rate)
        / (discount_rate - terminal_growth_rate)
    )
    present_terminal = terminal_value / ((Decimal("1") + discount_rate) ** len(free_cash_flows))
    enterprise_value = present_value + present_terminal
    equity_value = enterprise_value - net_debt
    return {
        "model": "dcf",
        "status": "ok",
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "formula": "sum(FCF_t/(1+r)^t) + terminal_value/(1+r)^n - net_debt",
        "calculated_at": datetime.now(UTC),
        "inputs": {
            "free_cash_flows": free_cash_flows,
            "discount_rate": discount_rate,
            "terminal_growth_rate": terminal_growth_rate,
            "net_debt": net_debt,
        },
    }


def multiple_valuation(
    model: str,
    numerator_value: Decimal,
    denominator_value: Decimal,
    multiple: Decimal,
) -> dict[str, Any]:
    if denominator_value == 0:
        return unavailable_payload(model, "Denominator is zero.")
    implied_value = denominator_value * multiple
    return {
        "model": model,
        "status": "ok",
        "implied_value": implied_value,
        "current_multiple": numerator_value / denominator_value,
        "selected_multiple": multiple,
        "formula": "denominator_value * selected_multiple",
        "calculated_at": datetime.now(UTC),
    }


def sensitivity_table(
    base_cash_flows: list[Decimal],
    discount_rates: list[Decimal],
    terminal_growth_rates: list[Decimal],
    net_debt: Decimal,
) -> list[dict[str, Any]]:
    rows = []
    for discount_rate in discount_rates:
        for terminal_growth_rate in terminal_growth_rates:
            rows.append(
                {
                    "discount_rate": discount_rate,
                    "terminal_growth_rate": terminal_growth_rate,
                    "result": dcf_valuation(
                        base_cash_flows, discount_rate, terminal_growth_rate, net_debt
                    ),
                }
            )
    return rows


def bull_base_bear_scenarios(
    base_free_cash_flow: Decimal,
    growth_rates: dict[str, Decimal],
    years: int = 3,
) -> dict[str, list[Decimal]]:
    scenarios: dict[str, list[Decimal]] = {}
    for scenario, growth_rate in growth_rates.items():
        values: list[Decimal] = []
        current = base_free_cash_flow
        for _ in range(years):
            current *= Decimal("1") + growth_rate
            values.append(current)
        scenarios[scenario] = values
    return scenarios


def reverse_dcf_required_growth(
    target_enterprise_value: Decimal,
    base_free_cash_flow: Decimal,
    discount_rate: Decimal,
    terminal_growth_rate: Decimal,
    years: int = 5,
) -> dict[str, Any]:
    if base_free_cash_flow <= 0:
        return unavailable_payload("reverse_dcf", "Base free cash flow must be positive.")
    low = Decimal("-0.50")
    high = Decimal("1.00")
    for _ in range(60):
        mid = (low + high) / Decimal("2")
        cash_flows = bull_base_bear_scenarios(base_free_cash_flow, {"required": mid}, years)[
            "required"
        ]
        value = dcf_valuation(cash_flows, discount_rate, terminal_growth_rate, Decimal("0"))
        enterprise_value = value.get("enterprise_value")
        if not isinstance(enterprise_value, Decimal):
            return value
        if enterprise_value < target_enterprise_value:
            low = mid
        else:
            high = mid
    return {
        "model": "reverse_dcf",
        "status": "ok",
        "required_growth_rate": (low + high) / Decimal("2"),
        "formula": "solve growth where DCF enterprise value equals target_enterprise_value",
        "calculated_at": datetime.now(UTC),
    }


def require_inputs(values: dict[str, MetricValue], *keys: str) -> dict[str, MetricValue]:
    return {key: values[key] for key in keys if key in values}


def divide(
    metric: str,
    numerator: MetricValue,
    denominator: MetricValue,
    formula: str,
    *,
    unit: str,
    inputs: dict[str, MetricValue],
) -> CalculationResult:
    try:
        if denominator.value == 0:
            raise DivisionByZero
        value = numerator.value / denominator.value
    except (DivisionByZero, InvalidOperation):
        return unavailable(metric, inputs, formula, "Denominator is zero or invalid.")
    return CalculationResult(
        metric=metric,
        status="ok",
        value=value,
        unit=unit,
        fiscal_period=numerator.fiscal_period,
        formula=formula,
        inputs=inputs,
        calculated_at=datetime.now(UTC),
    )


def unavailable(
    metric: str,
    values: dict[str, MetricValue],
    formula: str,
    message: str,
) -> CalculationResult:
    fiscal_period = next(iter(values.values())).fiscal_period if values else "unknown"
    return CalculationResult(
        metric=metric,
        status="unavailable",
        value=None,
        unit="n/a",
        fiscal_period=fiscal_period,
        formula=formula,
        inputs=values,
        calculated_at=datetime.now(UTC),
        message=f"无法可靠计算：{message}",
    )


def unavailable_payload(model: str, message: str) -> dict[str, Any]:
    return {
        "model": model,
        "status": "unavailable",
        "message": f"无法可靠计算：{message}",
        "calculated_at": datetime.now(UTC),
    }


def replace_value(result: CalculationResult, value: Decimal) -> CalculationResult:
    return CalculationResult(
        metric=result.metric,
        status=result.status,
        value=value,
        unit=result.unit,
        fiscal_period=result.fiscal_period,
        formula=result.formula,
        inputs=result.inputs,
        calculated_at=result.calculated_at,
        message=result.message,
    )
