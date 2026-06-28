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

AI_COMPANY_PROFILES = {
    "NVDA": {
        "categories": ["AI 加速芯片", "数据中心", "半导体平台"],
        "relevance_score": 96,
        "reason": "公司处于 AI 计算基础设施链条，需重点跟踪数据中心需求、供给瓶颈和毛利率持续性。",
    },
    "MSFT": {
        "categories": ["云平台", "AI 应用", "企业软件"],
        "relevance_score": 91,
        "reason": (
            "公司处于云基础设施和企业 AI 应用交叉位置，需跟踪云增长、"
            "AI 资本开支和 Copilot 商业化。"
        ),
    },
    "GOOGL": {
        "categories": ["云平台", "搜索广告", "AI 模型"],
        "relevance_score": 90,
        "reason": "公司同时暴露于 AI 搜索重构、云业务增长和自研 TPU 基础设施。",
    },
    "AMZN": {
        "categories": ["云平台", "电商基础设施", "AI 服务"],
        "relevance_score": 88,
        "reason": "公司 AI 相关性主要来自 AWS、算力基础设施和电商效率提升。",
    },
    "META": {
        "categories": ["互联网平台", "AI 推荐系统", "广告技术"],
        "relevance_score": 85,
        "reason": "公司 AI 相关性主要体现在推荐系统、广告效率、模型训练投入和算力资本开支。",
    },
    "AMD": {
        "categories": ["AI 加速芯片", "CPU/GPU", "半导体"],
        "relevance_score": 86,
        "reason": "公司是 AI GPU 和 CPU 竞争格局的重要变量，需跟踪产品迭代和生态迁移。",
    },
    "AVGO": {
        "categories": ["网络芯片", "ASIC", "半导体基础设施"],
        "relevance_score": 84,
        "reason": "公司与 AI 集群网络、定制 ASIC 和基础设施软件相关，需跟踪客户集中度和订单质量。",
    },
    "TSM": {
        "categories": ["晶圆代工", "先进制程", "先进封装"],
        "relevance_score": 93,
        "reason": "公司处于 AI 芯片制造关键环节，需跟踪先进制程产能、先进封装和客户订单结构。",
    },
    "ASML": {
        "categories": ["半导体设备", "EUV", "先进制程"],
        "relevance_score": 89,
        "reason": "公司处于先进制程设备关键环节，需跟踪订单、出口管制和客户资本开支周期。",
    },
    "PLTR": {
        "categories": ["AI 软件", "数据平台", "政府与企业软件"],
        "relevance_score": 82,
        "reason": "公司 AI 相关性来自企业数据平台和 AIP 商业化，需跟踪收入质量与客户扩张。",
    },
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
    generated_at = datetime.now(UTC)
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
        "exchange": first_string(profile_response.payload.get("exchanges")),
        "industry": profile_response.payload.get("sicDescription"),
        "description": profile_response.payload.get("category"),
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
    quality_scorecard = build_quality_scorecard(
        calculations,
        confidence,
        valuation,
        validation_payload,
    )
    research_standard = build_research_standard(archetype)
    business_analysis = build_business_analysis(profile, calculations, snapshot.current)
    industry_analysis = build_industry_analysis(profile, archetype)
    supply_chain_bottlenecks = build_supply_chain_bottlenecks(
        normalized_ticker,
        generated_at.date().isoformat(),
    )
    investment_committee = build_investment_committee(
        investor_decision,
        quality_scorecard,
        market_payload,
        validation_payload,
    )

    return {
        "ticker": normalized_ticker,
        "status": "completed",
        "generated_at": generated_at,
        "data_source": "SEC EDGAR / SEC XBRL",
        "company": profile,
        "ai_profile": AI_COMPANY_PROFILES.get(
            normalized_ticker,
            {
                "categories": ["待分类"],
                "relevance_score": 0,
                "reason": "该公司尚未进入第一阶段 AI 主题分类，需要人工补充。",
            },
        ),
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
        "investment_committee": investment_committee,
        "quality_scorecard": quality_scorecard,
        "research_standard": research_standard,
        "business_analysis": business_analysis,
        "industry_analysis": industry_analysis,
        "supply_chain_bottlenecks": supply_chain_bottlenecks,
        "research_report": build_report_sections(profile, calculations, valuation, sources),
        "quality_issues": quality_issues,
        "confidence_score": confidence,
        "sources": sources,
        "limitations": build_limitations(calculations, valuation),
    }


def first_string(value: object) -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return None


def archetype_value(archetype: object, key: str) -> object:
    if isinstance(archetype, dict):
        return archetype.get(key)
    return getattr(archetype, key, None)


def list_of_strings(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


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


def build_quality_scorecard(
    calculations: list[CalculationResult],
    confidence: Decimal,
    valuation: dict[str, object],
    validation: dict[str, object],
) -> list[dict[str, object]]:
    ok_metrics = {item.metric: item for item in calculations if item.status == "ok"}
    unavailable_count = len([item for item in calculations if item.status == "unavailable"])
    profitability_score = score_from_metric_count(
        ok_metrics,
        ["gross_margin", "operating_margin", "net_margin", "roe"],
        base=50,
        step=10,
    )
    balance_sheet_score = score_from_metric_count(
        ok_metrics,
        ["current_ratio", "debt_to_ebitda", "net_debt_to_ebitda", "interest_coverage"],
        base=45,
        step=10,
    )
    evidence_score = max(35, int(confidence * Decimal("100")) - unavailable_count * 3)
    valuation_score = 65 if valuation.get("status") == "completed" else 35
    validation_score = 70 if validation.get("status") == "ok" else 30
    return [
        {
            "label": "企业质量",
            "score": min(95, profitability_score),
            "rationale": "根据 SEC XBRL 可复算的利润率、ROE 和经营质量指标评分。",
        },
        {
            "label": "资产负债表",
            "score": min(90, balance_sheet_score),
            "rationale": "根据流动比率、债务覆盖和利息覆盖等可得指标评分，缺失项会扣分。",
        },
        {
            "label": "估值可用性",
            "score": valuation_score,
            "rationale": "只有自由现金流和价格数据齐全后，估值模块才可用于形成强结论。",
        },
        {
            "label": "历史验证",
            "score": validation_score,
            "rationale": "需要可追溯价格历史验证研究立场，未配置价格源时维持低分。",
        },
        {
            "label": "数据可信度",
            "score": min(95, evidence_score),
            "rationale": "基于 SEC 来源置信度、计算缺口和缺失指标数量综合评分。",
        },
    ]


def score_from_metric_count(
    metrics: dict[str, CalculationResult],
    required: list[str],
    *,
    base: int,
    step: int,
) -> int:
    return base + sum(step for metric in required if metric in metrics)


def build_research_standard(archetype: object) -> list[dict[str, object]]:
    archetype_name = str(archetype_value(archetype, "name") or "公司")
    return [
        {
            "title": "好生意",
            "principle": f"{archetype_name} 必须证明需求可持续、客户愿意付费且竞争优势不易被复制。",
            "checklist": [
                "收入增长是否来自真实需求，而不是一次性拉货或会计口径变化。",
                "毛利率和营业利润率是否能在竞争加剧时维持。",
                "客户、供应链和监管是否会削弱长期回报。",
            ],
        },
        {
            "title": "好公司",
            "principle": "管理层资本配置、现金流质量和资产负债表决定增长是否真正归属于股东。",
            "checklist": [
                "自由现金流是否能覆盖再投资和股东回报。",
                "股本摊薄、债务、库存和应收是否吞噬利润质量。",
                "公司披露是否足够透明，是否存在重大待验证事项。",
            ],
        },
        {
            "title": "好价格",
            "principle": "没有可靠价格和市值数据时，不得把企业质量直接翻译成投资吸引力。",
            "checklist": [
                "接入实时/历史价格后再计算 PE、EV/Sales、EV/FCF 和反向 DCF。",
                "至少比较悲观、基准、乐观三种情景。",
                "估值必须显示对增长率、利润率和折现率的敏感性。",
            ],
        },
    ]


def build_business_analysis(
    profile: dict[str, object],
    calculations: list[CalculationResult],
    current: dict[str, MetricValue],
) -> list[dict[str, object]]:
    company_name = str(profile["name"])
    revenue = current.get("revenue")
    gross_margin = find_calculation(calculations, "gross_margin")
    operating_margin = find_calculation(calculations, "operating_margin")
    net_margin = find_calculation(calculations, "net_margin")
    current_ratio = find_calculation(calculations, "current_ratio")
    return [
        {
            "title": "商业模式与盈利公式",
            "summary": (
                f"{company_name} 的在线报告当前基于 SEC 公司资料和 XBRL 财务事实生成。"
                "商业模式分析先识别收入、毛利、营业利润、净利润和现金流质量，"
                "再把缺失的经营指标列为待验证项。"
            ),
            "bullets": [
                value_sentence("收入规模", revenue),
                calculation_sentence("毛利率", gross_margin),
                calculation_sentence("营业利润率", operating_margin),
                calculation_sentence("净利率", net_margin),
                (
                    "待验证：收入分部、客户集中度、定价权和管理层对需求的表述"
                    "需从 10-K/10-Q 原文继续抽取。"
                ),
            ],
        },
        {
            "title": "盈利质量",
            "summary": "盈利质量重点看利润率是否由结构性优势支撑，而不是短期供需错配。",
            "bullets": [
                calculation_sentence("毛利率", gross_margin),
                calculation_sentence("营业利润率", operating_margin),
                "若毛利率高但库存、应收或客户集中度恶化，需要下调利润质量判断。",
                "当前系统不会把管理层口径直接当作事实；需要原文证据后才能升级结论。",
            ],
        },
        {
            "title": "现金流与资产负债表",
            "summary": "个人投资者需要判断利润是否转化为现金，以及增长是否依赖高风险融资。",
            "bullets": [
                calculation_sentence("流动比率", current_ratio),
                value_sentence("现金", current.get("cash")),
                value_sentence("总债务", current.get("total_debt")),
                "自由现金流、债务覆盖和营运资本指标缺失时，系统维持谨慎结论。",
            ],
        },
        {
            "title": "资本配置与股东回报",
            "summary": "资本配置模块关注再投资、回购、股权激励和长期 ROIC，而不是只看 EPS。",
            "bullets": [
                "待验证：回购、股权激励、并购和资本开支计划需要从申报文件原文抽取。",
                "若增长需要持续大幅增发或债务融资，企业质量评分应下调。",
                "当前缺少完整 ROIC 输入，不能可靠判断资本回报率。",
            ],
        },
    ]


def build_industry_analysis(
    profile: dict[str, object],
    archetype: object,
) -> list[dict[str, object]]:
    industry = str(profile.get("sic_description") or profile.get("industry") or "行业待确认")
    operating_metrics = list_of_strings(archetype_value(archetype, "operating_metrics"))
    valuation_priority = list_of_strings(archetype_value(archetype, "valuation_priority"))
    common_risks = list_of_strings(archetype_value(archetype, "common_risks"))
    peer_rules = list_of_strings(archetype_value(archetype, "peer_comparison_principles"))
    fallback_metrics = list_of_strings(archetype_value(archetype, "fallback_metrics"))
    not_applicable = list_of_strings(archetype_value(archetype, "not_applicable_metrics"))
    return [
        {
            "title": "行业定位",
            "summary": (
                f"SEC SIC 显示公司行业为 {industry}。"
                "行业分析以该分类和 archetype 规则为起点。"
            ),
            "bullets": [
                "这是结构化行业框架，不替代外部行业数据库或公司分部披露。",
                "下一步需要补充市场规模、增速、客户结构和同业财务指标。",
                "行业结论必须与公司申报、供应链数据和宏观数据交叉验证。",
            ],
        },
        {
            "title": "关键经营指标",
            "summary": "不同商业模式不能使用同一套指标强行比较，系统按 archetype 选择重点指标。",
            "bullets": operating_metrics
            + [
                "若上述指标未在 SEC XBRL 中出现，应从 10-K/10-Q 原文或公司材料抽取并保留证据链。",
            ],
        },
        {
            "title": "估值方法优先级",
            "summary": "估值方法必须匹配行业和商业模式，不能只看单一 PE。",
            "bullets": valuation_priority
            + [
                "当前市场价格源尚未配置，倍数估值只能列出方法，不能生成价格结论。",
                "DCF 需要自由现金流输入，缺失时必须显示无法可靠计算。",
            ],
        },
        {
            "title": "同业比较原则",
            "summary": "同业比较要先统一商业模式、收入结构、利润率口径和周期位置。",
            "bullets": peer_rules
            + [
                "待补充：同业池、基准指数、市场份额、毛利率和资本开支强度。",
                "不能把高增长公司和成熟周期公司直接用同一个倍数排序。",
            ],
        },
        {
            "title": "常见风险与替代指标",
            "summary": "数据缺失时，系统必须列出替代指标和不适用指标，避免误判。",
            "bullets": [
                "常见风险：" + join_or_na(common_risks),
                "替代指标：" + join_or_na(fallback_metrics),
                "不适用指标：" + join_or_na(not_applicable),
            ],
        },
    ]


def build_supply_chain_bottlenecks(ticker: str, evidence_date: str) -> list[dict[str, object]]:
    if ticker == "NVDA":
        return [
            {
                "stage": "先进封装 / CoWoS",
                "bottleneck": "AI 加速器需求增长可能受先进封装产能约束。",
                "expected_window": "未来 4-8 个季度需持续跟踪",
                "estimated_duration": "取决于 TSMC 与封测供应链扩产进度",
                "severity": "high",
                "involved_companies": ["NVIDIA", "TSMC", "ASE", "Amkor"],
                "likely_beneficiaries": ["TSMC", "先进封装设备与材料供应商"],
                "investment_implication": (
                    "若封装产能继续紧张，上游先进封装和相关设备链可能优先受益。"
                ),
                "watch_metrics": [
                    "CoWoS 产能扩张节奏",
                    "AI GPU 交期",
                    "数据中心收入增速",
                    "毛利率变化",
                ],
                "evidence_date": evidence_date,
                "confidence_score": 0.72,
            },
            {
                "stage": "HBM 高带宽内存",
                "bottleneck": "高端 AI GPU 需要 HBM 配套，内存供应可能影响交付节奏。",
                "expected_window": "未来 4-6 个季度需重点跟踪",
                "estimated_duration": "取决于 HBM3E/HBM4 良率和客户认证",
                "severity": "high",
                "involved_companies": ["NVIDIA", "SK hynix", "Samsung", "Micron"],
                "likely_beneficiaries": ["SK hynix", "Micron", "HBM 设备与材料供应商"],
                "investment_implication": "HBM 紧缺会把利润池向合格供应商和关键设备材料环节倾斜。",
                "watch_metrics": [
                    "HBM 合格供应商数量",
                    "HBM 位元供给增速",
                    "AI GPU 出货节奏",
                    "客户预付款与长约",
                ],
                "evidence_date": evidence_date,
                "confidence_score": 0.70,
            },
            {
                "stage": "数据中心电力与网络",
                "bottleneck": "AI 集群部署还受电力、液冷、网络交换和机柜交付约束。",
                "expected_window": "未来 6-12 个季度需持续观察",
                "estimated_duration": "取决于大型云厂商资本开支和数据中心建设周期",
                "severity": "medium",
                "involved_companies": [
                    "NVIDIA",
                    "Microsoft",
                    "Amazon",
                    "Google",
                    "Broadcom",
                ],
                "likely_beneficiaries": ["网络芯片供应商", "液冷与电力基础设施供应商"],
                "investment_implication": (
                    "若算力需求持续，瓶颈可能从芯片转向系统、电力和网络基础设施。"
                ),
                "watch_metrics": [
                    "云厂商 AI capex",
                    "以太网/InfiniBand 交换需求",
                    "数据中心上电周期",
                    "机柜功率密度",
                ],
                "evidence_date": evidence_date,
                "confidence_score": 0.64,
            },
        ]
    return [
        {
            "stage": "行业供应链",
            "bottleneck": "该公司供应链瓶颈需要结合 10-K/10-Q 原文和行业资料继续验证。",
            "expected_window": "未来 4-8 个季度",
            "estimated_duration": "待验证",
            "severity": "medium",
            "involved_companies": [ticker],
            "likely_beneficiaries": ["待行业资料确认"],
            "investment_implication": "在缺少外部供应链证据前，不形成受益者排序。",
            "watch_metrics": ["收入增速", "毛利率", "库存", "资本开支", "客户集中度"],
            "evidence_date": evidence_date,
            "confidence_score": 0.45,
        }
    ]


def build_investment_committee(
    investor_decision: dict[str, object],
    scorecard: list[dict[str, object]],
    market_price: dict[str, object],
    validation: dict[str, object],
) -> dict[str, object]:
    quality_score = next_score(scorecard, "企业质量")
    evidence_score = next_score(scorecard, "数据可信度")
    conclusion = str(investor_decision["stance"])
    if quality_score >= 75 and evidence_score >= 75 and market_price.get("status") == "ok":
        conclusion = "高优先级跟踪，等待估值安全边际确认"
    elif quality_score >= 65 and evidence_score >= 70:
        conclusion = "值得继续研究，但当前不能形成价格型结论"
    return {
        "conclusion": conclusion,
        "action": investor_decision["action"],
        "logic": investor_decision["why_it_matters"],
        "conditions_to_upgrade": [
            "接入可靠市场价格源，补齐 PE、EV/Sales、EV/FCF 与反向 DCF。",
            "从最新申报原文验证分部收入、客户集中度、供应链和管理层风险披露。",
            "完成与同业和指数的相对收益回测，且无未来数据泄露。",
            "自由现金流、ROIC、债务覆盖和股本摊薄指标可可靠计算。",
        ],
        "conditions_to_downgrade": [
            "SEC 数据出现冲突、过期或关键指标缺失无法解释。",
            "毛利率、营业利润率或现金转化显著恶化。",
            "关键客户削减订单、供应链瓶颈缓解导致议价能力下降。",
            "估值对增长假设高度敏感且缺少安全边际。",
            "历史验证显示申报后收益表现系统性偏弱。",
        ],
        "compliance_note": (
            "该结论是研究优先级与证据完整度判断，不是个性化买入、卖出或持有建议。"
        ),
        "validation_status": validation.get("status"),
    }


def find_calculation(
    calculations: list[CalculationResult],
    metric: str,
) -> CalculationResult | None:
    return next((item for item in calculations if item.metric == metric), None)


def calculation_sentence(label: str, calculation: CalculationResult | None) -> str:
    if calculation is None or calculation.status != "ok" or calculation.value is None:
        return f"{label}：当前 SEC 标准化数据不足，无法可靠计算。"
    return (
        f"{label}：{format_decimal(calculation.value)}，公式为 {calculation.formula}，"
        f"期间 {calculation.fiscal_period}。"
    )


def value_sentence(label: str, metric: MetricValue | None) -> str:
    if metric is None:
        return f"{label}：当前 SEC 标准化数据不足，无法可靠读取。"
    return (
        f"{label}：{format_decimal(metric.value)} {metric.unit}，期间 {metric.fiscal_period}。"
    )


def format_decimal(value: Decimal | int | float | str | None) -> str:
    if value is None:
        return "n/a"
    decimal = Decimal(str(value))
    if abs(decimal) >= Decimal("1000000000"):
        return f"{decimal / Decimal('1000000000'):.2f}B"
    if abs(decimal) >= Decimal("1000000"):
        return f"{decimal / Decimal('1000000'):.2f}M"
    return f"{decimal:.4f}".rstrip("0").rstrip(".")


def join_or_na(items: list[str]) -> str:
    return "、".join(items) if items else "待补充"


def next_score(scorecard: list[dict[str, object]], label: str) -> int:
    for item in scorecard:
        if item.get("label") == label:
            return int(item.get("score") or 0)
    return 0


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
            f"{company_name} 已通过 SEC submissions 公司资料识别。",
            "财务事实来自 SEC XBRL companyfacts，并保留来源 URL、哈希和拉取时间。",
        ],
        "calculations": [
            f"{calculation.metric}: {calculation.formula}" for calculation in ok_calculations[:8]
        ],
        "assumptions": assumption_values,
        "interpretation": [
            "本报告是确定性服务生成的第一版研究包，不由 LLM 直接计算财务数字。",
            "缺失指标保持不可用状态，不用猜测值替代。",
        ],
        "risks": [
            "SEC XBRL 不一定包含该商业模式所需的全部经营指标，需要继续抽取申报原文。",
            "估值结论对增长率、利润率、折现率和价格数据高度敏感。",
        ],
        "open_questions": [
            "需要继续阅读最新 10-K/10-Q 原文，验证分部、客户和供应链披露。",
            "需要接入可靠市场价格数据后，才能使用 PE、PS 或 EV 类倍数。",
        ],
        "sources": sources,
    }


def build_limitations(
    calculations: list[CalculationResult], valuation: dict[str, object]
) -> list[str]:
    limitations = [
        "系统不生成个性化买卖建议，也不输出收益承诺。",
        "市场价格数据尚未接入，因此不会生成交易倍数或价格目标。",
    ]
    unavailable = [
        calculation.metric for calculation in calculations if calculation.status == "unavailable"
    ]
    if unavailable:
        limitations.append(
            "当前 SEC 标准化数据仍缺少这些指标：" + ", ".join(unavailable[:8])
        )
    if valuation.get("status") == "partial":
        limitations.append("自由现金流不可可靠计算前，DCF 只能显示为不可用。")
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
