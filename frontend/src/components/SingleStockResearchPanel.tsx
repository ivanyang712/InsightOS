"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  CompanyResearchBundle,
  fetchCompanyResearch
} from "@/src/lib/companyResearch";

type ResearchState =
  | { status: "loading"; ticker: string }
  | { status: "ready"; data: CompanyResearchBundle };

type ResearchView = "summary" | "metrics" | "valuation" | "evidence";

const researchViews: Array<{ id: ResearchView; label: string }> = [
  { id: "summary", label: "研究摘要" },
  { id: "metrics", label: "财务指标" },
  { id: "valuation", label: "估值情景" },
  { id: "evidence", label: "证据链" }
];

export function SingleStockResearchPanel() {
  const [tickerInput, setTickerInput] = useState("AAPL");
  const [activeView, setActiveView] = useState<ResearchView>("summary");
  const [state, setState] = useState<ResearchState>({ status: "loading", ticker: "AAPL" });

  useEffect(() => {
    void runResearch("AAPL");
  }, []);

  async function runResearch(ticker: string) {
    const normalizedTicker = ticker.trim().toUpperCase() || "AAPL";
    setState({ status: "loading", ticker: normalizedTicker });
    const data = await fetchCompanyResearch(normalizedTicker);
    setTickerInput(data.report.ticker);
    setState({ status: "ready", data });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runResearch(tickerInput);
  }

  const report = state.status === "ready" ? state.data.report : null;
  const sourceLabel = state.status === "ready" ? state.data.source : "api";
  const metrics = useMemo(
    () => (report?.financial_quality ?? []).slice(0, 8),
    [report?.financial_quality]
  );

  return (
    <section className="research-panel">
      <div className="panel-heading">
        <p className="eyebrow">Single Stock Research</p>
        <h2>单只股票研究主链路</h2>
        <p>
          输入 ticker 后，系统会走 SEC profile、filings、XBRL facts、标准化财务事实、指标计算、
          DCF 情景和质量审计。
        </p>
      </div>

      <form className="ticker-form" onSubmit={submit}>
        <label htmlFor="ticker">Ticker</label>
        <input
          id="ticker"
          onChange={(event) => setTickerInput(event.target.value.toUpperCase())}
          placeholder="AAPL"
          value={tickerInput}
        />
        <button type="submit">Run Research</button>
      </form>

      {state.status === "loading" ? (
        <div className="workspace-panel">Loading {state.ticker} research packet...</div>
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
                CIK {report.company.cik} · {report.latest_annual_period} · Confidence{" "}
                {String(report.confidence_score)}
              </p>
            </div>
            <span className={sourceLabel === "api" ? "badge" : "badge warning"}>
              {sourceLabel === "api" ? "Live API" : "Synthetic fallback"}
            </span>
          </div>

          <div className="view-tabs" role="tablist" aria-label="Single stock research views">
            {researchViews.map((view) => (
              <button
                aria-selected={activeView === view.id}
                className={activeView === view.id ? "tab-button active" : "tab-button"}
                key={view.id}
                onClick={() => setActiveView(view.id)}
                role="tab"
                type="button"
              >
                {view.label}
              </button>
            ))}
          </div>

          {activeView === "summary" ? (
            <div className="workspace-grid">
              <article className="workspace-panel wide">
                <h3>Facts</h3>
                <ul>
                  {report.research_report.facts.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>Risks</h3>
                <ul>
                  {report.research_report.risks.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>Open Questions</h3>
                <ul>
                  {report.research_report.open_questions.map((item) => (
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
                  <h3>{metric.metric}</h3>
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
                <h3>DCF Bull / Base / Bear</h3>
                <div className="scenario-grid">
                  {Object.entries(report.valuation.scenarios ?? {}).map(([scenario, values]) => (
                    <div className="scenario-card" key={scenario}>
                      <strong>{scenario.toUpperCase()}</strong>
                      <span>{values.map(formatValue).join(" / ")}</span>
                    </div>
                  ))}
                </div>
              </article>
              <article className="workspace-panel">
                <h3>Assumptions</h3>
                <ul>
                  {Object.values(report.valuation.assumptions ?? {}).map((assumption) => (
                    <li key={assumption}>{assumption}</li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>Limitations</h3>
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
                <h3>SEC Filings</h3>
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
                <h3>Normalized Facts</h3>
                <ul>
                  {report.normalized_facts.slice(0, 6).map((fact) => (
                    <li key={`${fact.metric_name}-${fact.fiscal_period}`}>
                      {fact.metric_name}: {formatValue(fact.value)} {fact.unit}
                    </li>
                  ))}
                </ul>
              </article>
              <article className="workspace-panel">
                <h3>Sources</h3>
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
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
    notation: Math.abs(numeric) >= 1_000_000_000 ? "compact" : "standard"
  }).format(numeric);
}
