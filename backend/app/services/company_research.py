from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import cast

from app.connectors import ConnectorError
from app.connectors.market_prices import MarketPriceConnector, MarketPriceResponse, PriceBar
from app.connectors.sec import (
    NormalizedFiling,
    NormalizedFinancialFact,
    SecConnector,
    normalize_company_facts,
    normalize_filings,
)
from app.core.config import settings
from app.services.archetypes import match_company_archetype
from app.services.data_ingestion import raw_record_from_response
from app.services.financial_analysis import (
    CalculationResult,
    MetricValue,
    bull_base_bear_scenarios,
    calculate_financial_quality_metrics,
    dcf_valuation,
    unavailable_payload,
)
from app.services.quality import audit_ai_output, check_data_quality, estimate_confidence

TICKER_TO_CIK = {
    "NVDA": "0001045810",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
    "AMD": "0000002488",
    "AVGO": "0001730168",
    "TSM": "0001046179",
    "ASML": "0000937966",
    "PLTR": "0001321655",
}

SEC_TO_ENGINE_METRICS = {
    "revenues": "revenue",
    "gross_profit": "gross_profit",
    "operating_income": "operating_income",
    "net_income": "net_income",
    "cash": "cash",
    "current_assets": "current_assets",
    "current_liabilities": "current_liabilities",
    "shareholders_equity": "shareholders_equity",
    "operating_cash_flow": "operating_cash_flow",
    "capital_expenditure": "capital_expenditure",
    "shares_outstanding": "shares_outstanding",
}

DEBT_COMPONENTS = {"debt_current", "long_term_debt_noncurrent"}


class UnsupportedTickerError(ValueError):
    pass


@dataclass(frozen=True)
class FinancialInputSnapshot:
    current: dict[str, MetricValue]
    previous: dict[str, MetricValue] | None
    latest_year: int | None
    previous_year: int | None
    latest_period: str
    normalized_facts: list[NormalizedFinancialFact]


def run_single_company_research(
    ticker: str,
    *,
    connector: SecConnector | None = None,
    market_connector: MarketPriceConnector | None = None,
    include_market_data: bool = True,
) -> dict[str, object]:
    normalized_ticker = ticker.upper().strip()
    cik = TICKER_TO_CIK.get(normalized_ticker)
    if cik is None:
        raise UnsupportedTickerError(
            f"{normalized_ticker} is not in the MVP ticker map. "
            "Try NVDA, MSFT, GOOGL, AMZN, META, AMD, AVGO, TSM, ASML, or PLTR."
        )

    sec = connector or SecConnector()
    profile_response = sec.get_company_profile(cik)
    facts_response = sec.get_company_facts(cik)
    filings = normalize_filings(cik, profile_response.payload)
    normalized_facts = normalize_company_facts(facts_response)
    snapshot = build_financial_input_snapshot(normalized_facts)
    calculations = calculate_financial_quality_metrics(snapshot.current, snapshot.previous)
    quality_issues = check_data_quality(list(snapshot.current.values())) + audit_ai_output(
        "This report avoids personalized trading instructions and guaranteed-return language.",
        [True, True, True],
        calculations,
    )
    valuation = build_valuation(snapshot.current)
    archetype = match_company_archetype(
        normalized_ticker,
        str(profile_response.payload.get("sicDescription") or ""),
    )
    confidence = estimate_confidence(
        [
            Decimal(str(profile_response.metadata.confidence_score)),
            Decimal(str(facts_response.metadata.confidence_score)),
        ],
        len(quality_issues),
    )

    profile = {
        "name": profile_response.payload.get("name")
        or profile_response.payload.get("entityName")
        or normalized_ticker,
        "ticker": normalized_ticker,
        "cik": cik,
        "sic": profile_response.payload.get("sic"),
        "sic_description": profile_response.payload.get("sicDescription"),
        "archetype": archetype,
    }
    sources = [
        source_summary(
            "company_profile",
            profile_response.metadata.source_name,
            profile_response.metadata.source_url,
            profile_response.metadata.published_at,
            profile_response.metadata.retrieved_at,
            profile_response.metadata.source_hash,
            Decimal(str(profile_response.metadata.confidence_score)),
        ),
        source_summary(
            "company_facts",
            facts_response.metadata.source_name,
            facts_response.metadata.source_url,
            facts_response.metadata.published_at,
            facts_response.metadata.retrieved_at,
            facts_response.metadata.source_hash,
            Decimal(str(facts_response.metadata.confidence_score)),
        ),
    ]
    market_payload = build_unavailable_market_payload("市场价格数据源尚未配置。")
    validation_payload = build_unavailable_validation_payload(
        "市场价格数据源尚未配置，暂时无法做收益回测。"
    )
    if include_market_data and (
        market_connector is not None or settings.market_data_provider.lower() != "none"
    ):
        try:
            market_response = (market_connector or MarketPriceConnector()).get_daily_prices(
                normalized_ticker
            )
            market_payload = build_market_price_payload(market_response)
            validation_payload = build_filing_event_validation(filings, market_response)
            sources.append(
                source_summary(
                    "market_prices",
                    market_response.metadata.source_name,
                    market_response.metadata.source_url,
                    market_response.metadata.published_at,
                    market_response.metadata.retrieved_at,
                    market_response.metadata.source_hash,
                    Decimal(str(market_response.metadata.confidence_score)),
                )
            )
        except ConnectorError as error:
            market_payload = build_unavailable_market_payload(str(error))
            validation_payload = build_unavailable_validation_payload(str(error))
    investor_decision = build_investor_decision(
        profile,
        calculations,
        valuation,
        market_payload,
        validation_payload,
        confidence,
    )

    return {
        "ticker": normalized_ticker,
        "status": "completed",
        "generated_at": datetime.now(UTC),
        "data_source": "SEC EDGAR / SEC XBRL",
        "company": profile,
        "latest_annual_period": snapshot.latest_period,
        "filings": [filing_to_dict(filing) for filing in filings[:8]],
        "raw_records": [
            raw_record_from_response("sec", profile_response, normalized_status="profile_loaded"),
            raw_record_from_response("sec", facts_response, normalized_status="facts_normalized"),
        ],
        "normalized_facts": [
            fact_to_dict(fact)
            for fact in sorted(
                snapshot.normalized_facts,
                key=lambda item: (item.fiscal_year or 0, item.metric_name),
                reverse=True,
            )[:24]
        ],
        "financial_inputs": {
            "current": metric_values_to_payload(snapshot.current),
            "previous": metric_values_to_payload(snapshot.previous or {}),
        },
        "financial_quality": calculations,
        "valuation": valuation,
        "market_price": market_payload,
        "historical_validation": validation_payload,
        "investor_decision": investor_decision,
        "research_report": build_report_sections(profile, calculations, valuation, sources),
        "quality_issues": quality_issues,
        "confidence_score": confidence,
        "sources": sources,
        "limitations": build_limitations(calculations, valuation),
    }


def build_financial_input_snapshot(
    facts: list[NormalizedFinancialFact],
) -> FinancialInputSnapshot:
    annual_facts = [
        fact
        for fact in facts
        if fact.fiscal_year is not None and fact.fiscal_period.endswith("-FY")
    ]
    years = sorted({fact.fiscal_year for fact in annual_facts if fact.fiscal_year is not None})
    latest_year = years[-1] if years else None
    previous_year = years[-2] if len(years) > 1 else None
    current = metrics_for_year(annual_facts, latest_year)
    previous = metrics_for_year(annual_facts, previous_year) if previous_year is not None else None
    latest_period = f"FY{latest_year}" if latest_year is not None else "unknown"
    return FinancialInputSnapshot(
        current=current,
        previous=previous,
        latest_year=latest_year,
        previous_year=previous_year,
        latest_period=latest_period,
        normalized_facts=annual_facts,
    )


def metrics_for_year(
    facts: list[NormalizedFinancialFact],
    fiscal_year: int | None,
) -> dict[str, MetricValue]:
    if fiscal_year is None:
        return {}

    year_facts = [fact for fact in facts if fact.fiscal_year == fiscal_year]
    metrics: dict[str, MetricValue] = {}
    for sec_metric, engine_metric in SEC_TO_ENGINE_METRICS.items():
        fact = latest_fact(year_facts, sec_metric)
        if fact is not None:
            metrics[engine_metric] = metric_value(engine_metric, fact)

    debt_facts = [fact for fact in year_facts if fact.metric_name in DEBT_COMPONENTS]
    if debt_facts:
        total_debt = sum((fact.value for fact in debt_facts), Decimal("0"))
        first = debt_facts[0]
        metrics["total_debt"] = MetricValue(
            metric="total_debt",
            value=total_debt,
            currency=currency_from_unit(first.unit),
            unit=first.unit,
            fiscal_period=first.fiscal_period,
            source_hash=":".join(fact.source_hash for fact in debt_facts),
        )

    operating_cash_flow = metrics.get("operating_cash_flow")
    capital_expenditure = metrics.get("capital_expenditure")
    if operating_cash_flow is not None and capital_expenditure is not None:
        metrics["free_cash_flow"] = MetricValue(
            metric="free_cash_flow",
            value=operating_cash_flow.value - capital_expenditure.value,
            currency=operating_cash_flow.currency,
            unit=operating_cash_flow.unit,
            fiscal_period=operating_cash_flow.fiscal_period,
            source_hash=f"{operating_cash_flow.source_hash}:{capital_expenditure.source_hash}",
        )

    return metrics


def latest_fact(
    facts: list[NormalizedFinancialFact],
    metric_name: str,
) -> NormalizedFinancialFact | None:
    candidates = [fact for fact in facts if fact.metric_name == metric_name]
    if not candidates:
        return None
    return max(candidates, key=lambda fact: fact.filed_at or "")


def metric_value(metric: str, fact: NormalizedFinancialFact) -> MetricValue:
    return MetricValue(
        metric=metric,
        value=fact.value,
        currency=currency_from_unit(fact.unit),
        unit=fact.unit,
        fiscal_period=fact.fiscal_period,
        source_hash=fact.source_hash,
    )


def currency_from_unit(unit: str) -> str | None:
    return unit if len(unit) == 3 and unit.isalpha() else None


def build_valuation(current: dict[str, MetricValue]) -> dict[str, object]:
    free_cash_flow = current.get("free_cash_flow")
    if free_cash_flow is None:
        return {
            "status": "partial",
            "dcf": unavailable_payload("dcf", "Missing free cash flow."),
            "scenarios": {},
            "assumptions": {},
        }

    growth_rates = {
        "bear": Decimal("0.00"),
        "base": Decimal("0.03"),
        "bull": Decimal("0.06"),
    }
    scenarios = bull_base_bear_scenarios(free_cash_flow.value, growth_rates)
    total_debt = current.get("total_debt")
    cash = current.get("cash")
    net_debt = Decimal("0")
    if total_debt is not None and cash is not None:
        net_debt = total_debt.value - cash.value

    return {
        "status": "completed",
        "dcf": {
            scenario: dcf_valuation(cash_flows, Decimal("0.10"), Decimal("0.025"), net_debt)
            for scenario, cash_flows in scenarios.items()
        },
        "scenarios": scenarios,
        "assumptions": {
            "bear_growth": "0% FCF CAGR for three years",
            "base_growth": "3% FCF CAGR for three years",
            "bull_growth": "6% FCF CAGR for three years",
            "discount_rate": "10%",
            "terminal_growth_rate": "2.5%",
            "note": "Assumptions are editable placeholders, not investment advice.",
        },
    }


def build_market_price_payload(response: MarketPriceResponse) -> dict[str, object]:
    latest = response.bars[-1]
    first_1y = first_bar_on_or_after(response.bars, latest.date - timedelta(days=365))
    one_year_return = calculate_return(first_1y.close, latest.close) if first_1y else None
    return {
        "status": "ok",
        "ticker": response.ticker,
        "source_name": response.metadata.source_name,
        "source_url": response.metadata.source_url,
        "published_at": response.metadata.published_at,
        "retrieved_at": response.metadata.retrieved_at,
        "source_hash": response.metadata.source_hash,
        "confidence_score": Decimal(str(response.metadata.confidence_score)),
        "currency": "USD",
        "unit": "USD/share",
        "latest_date": latest.date.isoformat(),
        "latest_close": latest.close,
        "one_year_return": one_year_return,
        "trading_days": len(response.bars),
        "data_status": response.metadata.data_status,
        "note": "日收盘价来自在线市场数据源，不等同于实时逐笔行情。",
    }


def build_unavailable_market_payload(message: str) -> dict[str, object]:
    return {
        "status": "unavailable",
        "message": message,
        "note": (
            "在配置可靠在线价格源之前，系统不会生成市场倍数和价格回测结论。"
        ),
    }


def build_filing_event_validation(
    filings: list[NormalizedFiling],
    price_response: MarketPriceResponse,
) -> dict[str, object]:
    events: list[dict[str, object]] = []
    for filing in filings:
        if filing.filing_type not in {"10-K", "10-Q"}:
            continue
        try:
            filed_date = date.fromisoformat(filing.filed_at)
        except ValueError:
            continue
        entry = first_bar_on_or_after(price_response.bars, filed_date)
        if entry is None:
            continue
        event = {
            "filing_type": filing.filing_type,
            "filing_date": filing.filed_at,
            "entry_date": entry.date.isoformat(),
            "entry_price": entry.close,
            "return_90d": forward_return(price_response.bars, entry.date, 90),
            "return_180d": forward_return(price_response.bars, entry.date, 180),
            "return_365d": forward_return(price_response.bars, entry.date, 365),
        }
        if any(event[key] is not None for key in ("return_90d", "return_180d", "return_365d")):
            events.append(event)
        if len(events) >= 12:
            break

    completed_180d = [
        cast(Decimal, event["return_180d"]) for event in events if event["return_180d"] is not None
    ]
    if not completed_180d:
        return build_unavailable_validation_payload(
            "已完成的申报后价格窗口不足，暂时无法验证当前研究结论。"
        ) | {
            "events": events,
            "source_name": price_response.metadata.source_name,
            "source_url": price_response.metadata.source_url,
            "retrieved_at": price_response.metadata.retrieved_at,
            "source_hash": price_response.metadata.source_hash,
        }

    positive = [value for value in completed_180d if value > 0]
    median_180d = sorted(completed_180d)[len(completed_180d) // 2]
    hit_rate = Decimal(len(positive)) / Decimal(len(completed_180d))
    verdict = (
        "历史验证支持继续研究"
        if median_180d > Decimal("0") and hit_rate >= Decimal("0.50")
        else "历史验证不足，需要提高安全边际或等待更强证据"
    )
    return {
        "status": "ok",
        "methodology": (
            "仅使用当时已经公开的 10-K/10-Q 申报日期，从申报日后第一个交易日开始，"
            "计算后续 90/180/365 天日收盘价收益。"
        ),
        "source_name": price_response.metadata.source_name,
        "source_url": price_response.metadata.source_url,
        "retrieved_at": price_response.metadata.retrieved_at,
        "source_hash": price_response.metadata.source_hash,
        "events": events,
        "summary": {
            "sample_size": len(completed_180d),
            "median_180d_return": median_180d,
            "positive_180d_hit_rate": hit_rate,
        },
        "verdict": verdict,
        "limitations": [
            "这是事件研究验证，不是完整估值因子回测。",
            "它不能证明未来收益，也未纳入税费、滑点、仓位管理或相对基准收益。",
        ],
    }


def build_unavailable_validation_payload(message: str) -> dict[str, object]:
    return {
        "status": "unavailable",
        "message": message,
        "events": [],
        "summary": {},
        "limitations": [
            "历史验证需要可追溯的在线价格历史。",
            "未经验证的研究立场不能单独作为决策依据。",
        ],
    }


def build_investor_decision(
    profile: dict[str, object],
    calculations: list[CalculationResult],
    valuation: dict[str, object],
    market_price: dict[str, object],
    validation: dict[str, object],
    confidence: Decimal,
) -> dict[str, object]:
    ok_metrics = {
        calculation.metric: calculation
        for calculation in calculations
        if calculation.status == "ok"
    }
    missing_metrics = [
        calculation.metric
        for calculation in calculations
        if calculation.status == "unavailable"
    ]
    validation_ok = validation.get("status") == "ok"
    market_ok = market_price.get("status") == "ok"
    valuation_ready = valuation.get("status") == "completed"
    if confidence >= Decimal("0.80") and market_ok and validation_ok:
        stance = "高优先级跟踪"
        action = "可以进入个人研究候选池，但需要等待估值、增长和风险条件同时满足。"
    elif confidence >= Decimal("0.70") and market_ok:
        stance = "继续跟踪，暂不形成强结论"
        action = "先补齐估值与回测证据，再决定是否进入候选池。"
    else:
        stance = "证据不足"
        action = "当前只能阅读事实和风险，不能形成可执行研究结论。"

    revenue_growth = ok_metrics.get("revenue_growth")
    gross_margin = ok_metrics.get("gross_margin")
    price_context = (
        f"最新在线日收盘价为 {market_price.get('latest_close')} 美元/股，日期为 "
        f"{market_price.get('latest_date')}。"
        if market_ok
        else "在线市场价格暂不可用。"
    )
    return {
        "stance": stance,
        "action": action,
        "not_personalized_advice": (
            "这是研究流程输出，不是个性化买卖建议，也不是收益承诺。"
        ),
        "why_it_matters": [
            (
                f"{profile['name']} 需要同时评估需求持续性、毛利率可持续性、再投资空间"
                "和估值敏感性。"
            ),
            (
                "个人投资者不能只看公司质量，还需要价格纪律；好公司不等于任何价格都合理。"
            ),
            (
                "当数据缺口、低置信度或历史验证不足出现时，研究结论必须自动降级。"
            ),
        ],
        "current_price_context": price_context,
        "supporting_evidence": [
            (
                "收入增长指标状态："
                f"{status_label(revenue_growth.status if revenue_growth else None)}。"
            ),
            f"毛利率指标状态：{status_label(gross_margin.status if gross_margin else None)}。",
            f"估值引擎状态：{status_label(str(valuation.get('status')))}。",
            f"历史验证状态：{status_label(str(validation.get('status')))}。",
        ],
        "decision_rules": [
            "只有收入质量、现金转化和利润率可持续性都有来源支持时，才允许上调研究优先级。",
            "必须先写清悲观情景和下行空间，再判断估值是否有吸引力。",
            "关键指标缺失、过期、冲突，或申报后 180 天历史验证偏弱时，自动下调结论。",
            "在实时价格、市值、股本和基准对比接入前，不输出仓位建议。",
        ],
        "must_verify_next": [
            "从最新 10-K/10-Q 原文验证分部收入质量和客户集中度。",
            "补齐当前市值、摊薄股本、净现金/净债务，以及不依赖卖方一致预期的估值假设。",
            "用非公司来源验证供应链瓶颈和交期指标。",
            "补充相对 Nasdaq 100 或半导体同业的基准收益验证。",
        ],
        "missing_evidence": missing_metrics[:10],
        "valuation_ready": valuation_ready,
    }


def first_bar_on_or_after(bars: list[PriceBar], target: date) -> PriceBar | None:
    for bar in bars:
        if bar.date >= target:
            return bar
    return None


def forward_return(bars: list[PriceBar], start: date, days: int) -> Decimal | None:
    entry = first_bar_on_or_after(bars, start)
    exit_bar = first_bar_on_or_after(bars, date.fromordinal(start.toordinal() + days))
    if entry is None or exit_bar is None:
        return None
    return calculate_return(entry.close, exit_bar.close)


def calculate_return(start: Decimal, end: Decimal) -> Decimal | None:
    if start == 0:
        return None
    return (end - start) / start


def status_label(status: str | None) -> str:
    labels = {
        "ok": "可用",
        "completed": "完成",
        "partial": "部分可用",
        "unavailable": "不可用",
    }
    return labels.get(status or "unavailable", status or "不可用")


def build_report_sections(
    profile: dict[str, object],
    calculations: list[CalculationResult],
    valuation: dict[str, object],
    sources: list[dict[str, object]],
) -> dict[str, object]:
    company_name = str(profile["name"])
    ok_calculations = [calculation for calculation in calculations if calculation.status == "ok"]
    assumptions = valuation.get("assumptions")
    assumption_values = (
        [str(value) for value in cast(dict[str, object], assumptions).values()]
        if isinstance(assumptions, dict)
        else []
    )
    return {
        "facts": [
            f"{company_name} is resolved from SEC company submissions.",
            "Financial facts are normalized from SEC XBRL companyfacts.",
        ],
        "calculations": [
            f"{calculation.metric}: {calculation.formula}" for calculation in ok_calculations[:8]
        ],
        "assumptions": assumption_values,
        "interpretation": [
            "The report is a deterministic first-pass research packet.",
            "Unavailable metrics are left unavailable rather than estimated.",
        ],
        "risks": [
            "Filings may not provide every operating metric required for this archetype.",
            "Valuation output is sensitive to placeholder growth and discount-rate assumptions.",
        ],
        "open_questions": [
            "Review the latest 10-K text for segment, customer, and supply-chain disclosures.",
            "Add market price data before using PE, PS, or EV-based multiples.",
        ],
        "sources": sources,
    }


def build_limitations(
    calculations: list[CalculationResult], valuation: dict[str, object]
) -> list[str]:
    limitations = [
        "No personalized buy/sell advice is generated.",
        "Market price data is not connected yet, so trading multiples are not produced.",
    ]
    unavailable = [
        calculation.metric for calculation in calculations if calculation.status == "unavailable"
    ]
    if unavailable:
        limitations.append(
            "Metrics unavailable from current normalized SEC facts: " + ", ".join(unavailable[:8])
        )
    if valuation.get("status") == "partial":
        limitations.append("DCF is unavailable until free cash flow can be calculated.")
    return limitations


def source_summary(
    source_type: str,
    source_name: str,
    source_url: str,
    published_at: datetime,
    retrieved_at: datetime,
    source_hash: str,
    confidence_score: Decimal,
) -> dict[str, object]:
    return {
        "source_type": source_type,
        "source_name": source_name,
        "source_url": source_url,
        "published_at": published_at,
        "retrieved_at": retrieved_at,
        "source_hash": source_hash,
        "confidence_score": confidence_score,
    }


def filing_to_dict(filing: NormalizedFiling) -> dict[str, object]:
    return {
        "accession_number": filing.accession_number,
        "filing_type": filing.filing_type,
        "filed_at": filing.filed_at,
        "period_end_date": filing.period_end_date,
        "primary_document_url": filing.primary_document_url,
    }


def fact_to_dict(fact: NormalizedFinancialFact) -> dict[str, object]:
    return {
        "metric_name": fact.metric_name,
        "value": fact.value,
        "unit": fact.unit,
        "fiscal_period": fact.fiscal_period,
        "fiscal_year": fact.fiscal_year,
        "filed_at": fact.filed_at,
        "source_url": fact.source_url,
        "source_hash": fact.source_hash,
    }


def metric_values_to_payload(values: dict[str, MetricValue]) -> dict[str, dict[str, object]]:
    return {
        key: {
            "metric": value.metric,
            "value": value.value,
            "currency": value.currency,
            "unit": value.unit,
            "fiscal_period": value.fiscal_period,
            "source_hash": value.source_hash,
        }
        for key, value in values.items()
    }


def research_error_payload(ticker: str, error: ConnectorError) -> dict[str, object]:
    return {
        "ticker": ticker.upper(),
        "status": "error",
        "message": str(error),
        "generated_at": datetime.now(UTC),
    }
