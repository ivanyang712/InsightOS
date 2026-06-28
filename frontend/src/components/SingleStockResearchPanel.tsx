"use client";

import { FormEvent, MouseEvent, useEffect, useMemo, useState } from "react";

import {
  CompanyResearchBundle,
  fetchCompanyResearch,
  supportedFallbackTickers
} from "@/src/lib/companyResearch";

type ResearchState =
  | { status: "loading"; ticker: string }
  | { status: "ready"; data: CompanyResearchBundle }
  | { status: "error"; ticker: string; message: string };

type ResearchView =
  | "committee"
  | "business"
  | "industry"
  | "bottlenecks"
  | "validation"
  | "metrics"
  | "valuation"
  | "risk"
  | "evidence";

const researchViews: Array<{ id: ResearchView; label: string }> = [
  { id: "committee", label: "投资结论" },
  { id: "business", label: "商业模式" },
  { id: "industry", label: "产业分析" },
  { id: "bottlenecks", label: "产业瓶颈" },
  { id: "validation", label: "价格与回测" },
  { id: "metrics", label: "财务质量" },
  { id: "valuation", label: "估值框架" },
  { id: "risk", label: "反证风险" },
  { id: "evidence", label: "证据链" }
];

type SingleStockResearchPanelProps = {
  initialTicker: string;
  initialView?: string;
  initialResearch?: CompanyResearchBundle;
  initialError?: {
    ticker: string;
    message: string;
  };
};

export function SingleStockResearchPanel({
  initialTicker,
  initialView,
  initialResearch,
  initialError
}: SingleStockResearchPanelProps) {
  const normalizedInitialTicker = normalizeTicker(initialTicker);
  const [tickerInput, setTickerInput] = useState(normalizedInitialTicker);
  const [activeView, setActiveView] = useState<ResearchView>(normalizeResearchView(initialView));
  const [state, setState] = useState<ResearchState>(
    initialResearch
      ? { status: "ready", data: initialResearch }
      : initialError
        ? { status: "error", ticker: initialError.ticker, message: initialError.message }
        : { status: "loading", ticker: normalizedInitialTicker }
  );

  useEffect(() => {
    if (!initialResearch && !initialError) {
      void runResearch(normalizedInitialTicker);
    }
  }, [initialError, initialResearch, normalizedInitialTicker]);

  async function runResearch(ticker: string) {
    const normalizedTicker = normalizeTicker(ticker);
    setState({ status: "loading", ticker: normalizedTicker });
    try {
      const data = await fetchCompanyResearch(normalizedTicker);
      setTickerInput(data.report.ticker);
      setState({ status: "ready", data });
    } catch (error) {
      setTickerInput(normalizedTicker);
      setState({
        status: "error",
        ticker: normalizedTicker,
        message: error instanceof Error ? error.message : "在线数据连接失败"
      });
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runResearch(tickerInput);
  }

  function switchView(
    event: MouseEvent<HTMLAnchorElement>,
    view: ResearchView,
    ticker: string
  ) {
    event.preventDefault();
    setActiveView(view);
    window.history.replaceState(
      null,
      "",
      `/?ticker=${encodeURIComponent(ticker)}&view=${view}#single-stock`
    );
  }

  const report = state.status === "ready" ? state.data.report : null;
  const sourceLabel = state.status === "ready" ? state.data.source : "api";
  const metrics = useMemo(
    () => (report?.financial_quality ?? []).slice(0, 8),
    [report?.financial_quality]
  );

  return (
    <section className="research-panel" id="single-stock">
      <div className="panel-heading">
        <p className="eyebrow">单股研究</p>
        <h2>单只股票研究主链路</h2>
        <p>
          输入 ticker 后，系统会走 SEC profile、filings、XBRL facts、标准化财务事实、指标计算、
          DCF 情景和质量审计。
        </p>
      </div>

      <form action="/" className="ticker-form" method="get" onSubmit={submit}>
        <label htmlFor="ticker">股票代码</label>
        <input
          id="ticker"
          name="ticker"
          onChange={(event) => setTickerInput(event.target.value.toUpperCase())}
          placeholder="AAPL"
          value={tickerInput}
        />
        <button type="submit">生成研究结果</button>
      </form>

      <div className="ticker-shortcuts" aria-label="Supported online tickers">
        {supportedFallbackTickers.map((ticker) => (
          <a
            href={`/?ticker=${ticker}#single-stock`}
            key={ticker}
            onClick={(event) => {
              event.preventDefault();
              void runResearch(ticker);
            }}
          >
            {ticker}
          </a>
        ))}
      </div>

      {state.status === "loading" ? (
        <div className="workspace-panel">正在连接 SEC EDGAR / XBRL，生成 {state.ticker} 在线研究包...</div>
      ) : null}

      {state.status === "error" ? (
        <div className="workspace-panel wide warning-panel">
          <h3>{state.ticker} 在线数据暂不可用</h3>
          <p>{state.message}</p>
          <ul>
            <li>请确认后端服务已启动：http://127.0.0.1:8000/health。</li>
            <li>SEC 数据需要可识别 User-Agent，并且网络能访问 data.sec.gov。</li>
            <li>页面不会再自动使用离线演示数据替代在线数据。</li>
          </ul>
        </div>
      ) : null}

      {report ? (
        <>
          <div className="research-header">
            <div>
              <p className="eyebrow">{report.data_source}</p>
              <h3>
                {report.company.name} ({report.ticker})
              </h3>
              <p>
                CIK {report.company.cik} · {report.latest_annual_period} · 可信度{" "}
                {String(report.confidence_score)}
              </p>
              <p>
                {report.company.exchange ?? "交易所待确认"} · {report.company.industry ?? "行业待确认"} · AI 相关性{" "}
                {report.ai_profile?.relevance_score ?? 0}/100
              </p>
              <div className="category-strip">
                {(report.ai_profile?.categories ?? []).map((category) => (
                  <span key={category}>{category}</span>
                ))}
              </div>
              {report.ai_profile?.reason ? <p>{report.ai_profile.reason}</p> : null}
            </div>
            <span className={sourceLabel === "api" ? "badge" : "badge warning"}>
              {sourceLabel === "api" ? "实时 API" : "本地样例"}
            </span>
          </div>

          <div className="view-tabs" role="tablist" aria-label="Single stock research views">
            {researchViews.map((view) => (
              <a
                aria-selected={activeView === view.id}
                className={activeView === view.id ? "tab-button active" : "tab-button"}
                href={`/?ticker=${encodeURIComponent(report.ticker)}&view=${view.id}#single-stock`}
                key={view.id}
                onClick={(event) => switchView(event, view.id, report.ticker)}
                role="tab"
              >
                {view.label}
              </a>
            ))}
          </div>

          {activeView === "committee" ? (
            <div className="workspace-grid">
              <article className="workspace-panel wide committee-panel">
                <p className="eyebrow">投资委员会结论</p>
                <h3>{report.investment_committee?.conclusion ?? "证据不足，无法形成研究结论"}</h3>
                <p className="decision-callout">
                  {report.investor_decision?.action ??
                    report.investment_committee?.action ??
                    "请先补齐可验证数据。"}
                </p>
                <ul>
                  {(
                    report.investor_decision?.why_it_matters ??
                    report.investment_committee?.logic ??
                    report.research_report.interpretation
                  ).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                </ul>
                <small>
                  {report.investor_decision?.not_personalized_advice ??
                    report.investment_committee?.compliance_note}
                </small>
              </article>
              <article className="workspace-panel">
                <h3>个人投资者决策框架</h3>
                <p className="metric-value">{report.investor_decision?.stance ?? "待验证"}</p>
                <p>{report.investor_decision?.current_price_context}</p>
                <ul>
                  {(report.investor_decision?.supporting_evidence ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>评分矩阵</h3>
                <div className="score-table">
                  {(report.quality_scorecard ?? []).map((item) => (
                    <div className="score-row" key={item.label}>
                      <strong>
                        {item.label}: {item.score}/100
                      </strong>
                      <span>{item.rationale}</span>
                    </div>
                  ))}
                </div>
              </article>
              <article className="workspace-panel">
                <h3>研究标准</h3>
                <ul>
                  {(report.research_standard ?? []).map((item) => (
                    <li key={item.title}>
                      <strong>{item.title}</strong>: {item.principle}
                    </li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel wide">
                <h3>产业瓶颈速览</h3>
                <ul>
                  {(report.supply_chain_bottlenecks ?? []).slice(0, 3).map((item) => (
                    <li key={`${item.stage}-${item.expected_window}`}>
                      <strong>{item.stage}</strong>: {item.expected_window}，预计持续 {item.estimated_duration}。
                      潜在受益者：{item.likely_beneficiaries.join(" / ")}。
                    </li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}

          {activeView === "business" ? (
            <div className="workspace-grid">
              {(report.business_analysis ?? []).map((section) => (
                <article
                  className={section.title === "商业模式与盈利公式" ? "workspace-panel wide" : "workspace-panel"}
                  key={section.title}
                >
                  <h3>{section.title}</h3>
                  <p>{section.summary}</p>
                  <ul>
                    {section.bullets.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          ) : null}

          {activeView === "industry" ? (
            <div className="workspace-grid">
              {(report.industry_analysis ?? []).map((section) => (
                <article className="workspace-panel wide" key={section.title}>
                  <h3>{section.title}</h3>
                  <p>{section.summary}</p>
                  <ul>
                    {section.bullets.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              ))}
              <article className="workspace-panel">
                <h3>已验证事实</h3>
                <ul>
                  {report.research_report.facts.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}

          {activeView === "bottlenecks" ? (
            <div className="workspace-grid">
              {(report.supply_chain_bottlenecks ?? []).map((item) => (
                <article className="workspace-panel wide bottleneck-card" key={`${item.stage}-${item.bottleneck}`}>
                  <div className="bottleneck-header">
                    <div>
                      <p className="eyebrow">{item.stage}</p>
                      <h3>{item.bottleneck}</h3>
                    </div>
                    <span className={`severity-badge severity-${item.severity}`}>{severityLabel(item.severity)}</span>
                  </div>
                  <div className="bottleneck-meta">
                    <span>窗口：{item.expected_window}</span>
                    <span>持续：{item.estimated_duration}</span>
                    <span>置信度：{Math.round(item.confidence_score * 100)}%</span>
                  </div>
                  <p className="decision-callout">{item.investment_implication}</p>
                  <div className="bottleneck-columns">
                    <div>
                      <h4>涉及公司</h4>
                      <p>{item.involved_companies.join(" / ")}</p>
                    </div>
                    <div>
                      <h4>潜在受益者</h4>
                      <p>{item.likely_beneficiaries.join(" / ")}</p>
                    </div>
                  </div>
                  <h4>跟踪指标</h4>
                  <ul>
                    {item.watch_metrics.map((metric) => (
                      <li key={metric}>{metric}</li>
                    ))}
                  </ul>
                  <small>证据日期 / 假设更新时间：{item.evidence_date}</small>
                </article>
              ))}
            </div>
          ) : null}

          {activeView === "validation" ? (
            <div className="workspace-grid">
              <article className="workspace-panel">
                <h3>在线价格摘要</h3>
                {report.market_price?.status === "ok" ? (
                  <>
                    <p className="metric-value">
                      {formatValue(report.market_price.latest_close ?? "")}{" "}
                      {report.market_price.currency ?? "USD"}
                    </p>
                    <p>
                      日期：{report.market_price.latest_date} · 1 年变化：
                      {formatPercent(report.market_price.one_year_return)}
                    </p>
                    <small>
                      {report.market_price.source_name} · {report.market_price.retrieved_at}
                    </small>
                  </>
                ) : (
                  <p className="warning-text">
                    {report.market_price?.message ?? "在线价格暂不可用"}
                  </p>
                )}
              </article>
              <article className="workspace-panel wide">
                <h3>历史事件验证</h3>
                <p className="decision-callout">
                  {report.historical_validation?.verdict ??
                    report.historical_validation?.message ??
                    "历史验证暂不可用"}
                </p>
                <p>{report.historical_validation?.methodology}</p>
                <div className="score-table">
                  <div className="score-row">
                    <strong>样本数</strong>
                    <span>{report.historical_validation?.summary.sample_size ?? "不足"}</span>
                  </div>
                  <div className="score-row">
                    <strong>180 天中位回报</strong>
                    <span>
                      {formatPercent(report.historical_validation?.summary.median_180d_return)}
                    </span>
                  </div>
                  <div className="score-row">
                    <strong>180 天胜率</strong>
                    <span>
                      {formatPercent(report.historical_validation?.summary.positive_180d_hit_rate)}
                    </span>
                  </div>
                </div>
              </article>
              <article className="workspace-panel wide">
                <h3>回测事件样本</h3>
                <div className="compact-table">
                  {(report.historical_validation?.events ?? []).slice(0, 6).map((event) => (
                    <div className="table-row" key={`${event.filing_type}-${event.filing_date}`}>
                      <strong>{event.filing_type}</strong>
                      <span>{event.entry_date}</span>
                      <span>入场 {formatValue(event.entry_price)}</span>
                      <span>180 天 {formatPercent(event.return_180d)}</span>
                    </div>
                  ))}
                </div>
              </article>
              <article className="workspace-panel">
                <h3>决策纪律</h3>
                <ul>
                  {(report.investor_decision?.decision_rules ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>下一步必须验证</h3>
                <ul>
                  {(report.investor_decision?.must_verify_next ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}

          {activeView === "risk" ? (
            <div className="workspace-grid">
              <article className="workspace-panel wide">
                <h3>反证与降级条件</h3>
                <ul>
                  {(report.investment_committee?.conditions_to_downgrade ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>升级条件</h3>
                <ul>
                  {(report.investment_committee?.conditions_to_upgrade ?? []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>待验证问题与风险</h3>
                <ul>
                  {[...report.research_report.risks, ...report.research_report.open_questions].map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}

          {activeView === "metrics" ? (
            <div className="workspace-grid">
              {metrics.map((metric) => (
                <article className="workspace-panel" key={metric.metric}>
                  <h3>{metricLabel(metric.metric)}</h3>
                  <p className={metric.status === "ok" ? "metric-value" : "warning-text"}>
                    {metric.value === null ? "无法可靠计算" : formatValue(metric.value)}
                  </p>
                  <small>{metric.formula}</small>
                </article>
              ))}
            </div>
          ) : null}

          {activeView === "valuation" ? (
            <div className="workspace-grid">
              <article className="workspace-panel wide">
                <h3>DCF 乐观 / 基准 / 悲观情景</h3>
                <div className="scenario-grid">
                  {Object.entries(report.valuation.scenarios ?? {}).map(([scenario, values]) => (
                    <div className="scenario-card" key={scenario}>
                      <strong>{scenarioLabel(scenario)}</strong>
                      <span>{values.map(formatValue).join(" / ")}</span>
                    </div>
                  ))}
                </div>
              </article>
              <article className="workspace-panel">
                <h3>关键假设</h3>
                <ul>
                  {Object.values(report.valuation.assumptions ?? {}).map((assumption) => (
                    <li key={assumption}>{assumption}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>当前限制</h3>
                <ul>
                  {report.limitations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}

          {activeView === "evidence" ? (
            <div className="workspace-grid">
              <article className="workspace-panel wide">
                <h3>SEC 申报文件</h3>
                <div className="compact-table">
                  {report.filings.slice(0, 5).map((filing) => (
                    <div className="table-row" key={filing.accession_number}>
                      <strong>{filing.filing_type}</strong>
                      <span>{filing.filed_at}</span>
                      <span>{filing.accession_number}</span>
                    </div>
                  ))}
                </div>
              </article>
              <article className="workspace-panel">
                <h3>标准化财务事实</h3>
                <ul>
                  {report.normalized_facts.slice(0, 6).map((fact) => (
                    <li key={`${fact.metric_name}-${fact.fiscal_period}`}>
                      {metricLabel(fact.metric_name)}: {formatValue(fact.value)} {fact.unit}
                    </li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>来源与置信度</h3>
                <ul>
                  {report.sources.map((source) => (
                    <li key={source.source_hash}>
                      {source.source_name} · {String(source.confidence_score)}
                    </li>
                  ))}
                </ul>
              </article>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

function formatValue(value: string | number) {
  if (value === "") {
    return "n/a";
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
    notation: Math.abs(numeric) >= 1_000_000_000 ? "compact" : "standard"
  }).format(numeric);
}

function formatPercent(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return "样本不足";
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return new Intl.NumberFormat("zh-CN", {
    maximumFractionDigits: 1,
    style: "percent"
  }).format(numeric);
}

function normalizeTicker(ticker: string): string {
  return ticker.trim().toUpperCase() || "NVDA";
}

function normalizeResearchView(view?: string): ResearchView {
  if (researchViews.some((item) => item.id === view)) {
    return view as ResearchView;
  }
  return "committee";
}

function metricLabel(metric: string) {
  const labels: Record<string, string> = {
    revenue_growth: "收入增长率",
    gross_margin: "毛利率",
    operating_margin: "营业利润率",
    net_margin: "净利率",
    free_cash_flow_margin: "自由现金流率",
    inventory_turnover: "库存周转率",
    net_interest_margin: "净息差",
    research_packet: "研究包状态",
    revenues: "收入",
    gross_profit: "毛利润",
    operating_income: "营业利润",
    net_income: "净利润",
    free_cash_flow: "自由现金流"
  };
  return labels[metric] ?? metric;
}

function scenarioLabel(scenario: string) {
  const labels: Record<string, string> = {
    bear: "悲观情景",
    base: "基准情景",
    bull: "乐观情景"
  };
  return labels[scenario] ?? scenario.toUpperCase();
}

function severityLabel(severity: string) {
  const labels: Record<string, string> = {
    low: "低",
    medium: "中",
    high: "高",
    critical: "关键瓶颈"
  };
  return labels[severity] ?? severity;
}
