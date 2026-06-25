"use client";

import { useEffect, useState } from "react";

import { fetchDemoBundle, fallbackDemoBundle } from "@/src/lib/demo";

type DemoBundle = Awaited<ReturnType<typeof fetchDemoBundle>>;

type DemoState =
  | { status: "loading" }
  | { status: "ready"; data: DemoBundle };

type DemoView = "company" | "valuation" | "industry" | "comparison" | "quality";

const views: Array<{ id: DemoView; label: string }> = [
  { id: "company", label: "公司研究" },
  { id: "valuation", label: "估值情景" },
  { id: "industry", label: "行业地图" },
  { id: "comparison", label: "同业对比" },
  { id: "quality", label: "质量审计" }
];

export function DemoResearchPanel() {
  const [state, setState] = useState<DemoState>({ status: "loading" });
  const [activeView, setActiveView] = useState<DemoView>("company");

  useEffect(() => {
    let active = true;
    fetchDemoBundle()
      .then((data) => {
        if (active) {
          setState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        console.warn("Demo API unavailable, using synthetic fallback.", error);
        if (active) {
          setState({ status: "ready", data: fallbackDemoBundle });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (state.status === "loading") {
    return <section className="demo-panel">Loading research demo...</section>;
  }

  const { nvidia, industry, comparison } = state.data;
  const sourceLabel = state.data.source === "api" ? "Backend API" : "Synthetic fallback";

  return (
    <section className="demo-panel">
      <div className="panel-heading">
        <p className="eyebrow">Research Workflow Demo</p>
        <h2>InsightOS 投研工作台体验</h2>
        <p>{nvidia.demo_notice}</p>
        <span className={state.data.source === "api" ? "badge" : "badge warning"}>
          {sourceLabel}
        </span>
      </div>

      <div className="view-tabs" role="tablist" aria-label="InsightOS demo views">
        {views.map((view) => (
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

      {activeView === "company" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">Company Research Agent</p>
            <h3>{nvidia.company?.name ?? "Nvidia"} Research Packet</h3>
            <p>{nvidia.research_output.executive_summary}</p>
            <div className="metric-strip">
              <span>Archetype: {nvidia.company?.archetype?.name ?? "Semiconductor"}</span>
              <span>Confidence: {nvidia.agent_report?.confidence_score ?? "0.9000"}</span>
              <span>Advice language: blocked</span>
            </div>
          </article>
          <article className="workspace-panel">
            <h3>Risks</h3>
            <ul>
              {nvidia.research_output.risks.slice(0, 4).map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          </article>
          <article className="workspace-panel">
            <h3>Open Questions</h3>
            <ul>
              {(nvidia.agent_report?.open_questions ?? []).map((question) => (
                <li key={question}>{question}</li>
              ))}
            </ul>
          </article>
        </div>
      ) : null}

      {activeView === "valuation" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">Deterministic Calculation Service</p>
            <h3>DCF / EV-Sales / PE 情景</h3>
            <div className="scenario-grid">
              {Object.entries(nvidia.research_output.bull_base_bear).map(([scenario, values]) => (
                <div className="scenario-card" key={scenario}>
                  <strong>{scenario.toUpperCase()}</strong>
                  <span>{values.map(formatNumber).join(" / ")}</span>
                </div>
              ))}
            </div>
          </article>
          {(nvidia.research_output.financial_quality ?? []).slice(0, 4).map((metric) => (
            <article className="workspace-panel" key={metric.metric}>
              <h3>{metric.metric}</h3>
              <p className={metric.status === "ok" ? "metric-value" : "warning-text"}>
                {metric.value === null ? "无法可靠计算" : formatNumber(metric.value)}
              </p>
              <small>{metric.formula}</small>
            </article>
          ))}
        </div>
      ) : null}

      {activeView === "industry" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">Industry Research Agent</p>
            <h3>{industry.industry}</h3>
            <p>{industry.competitive_landscape?.join(" / ")}</p>
          </article>
          {Object.entries(industry.value_chain_map ?? {}).map(([layer, companies]) => (
            <article className="workspace-panel" key={layer}>
              <h3>{layer}</h3>
              <p>{companies.join(", ")}</p>
            </article>
          ))}
          <article className="workspace-panel">
            <h3>Cycle Indicators</h3>
            <p>{industry.cycle_indicators.join(", ")}</p>
          </article>
          <article className="workspace-panel">
            <h3>Tracking Metrics</h3>
            <p>{industry.tracking_metrics.join(", ")}</p>
          </article>
        </div>
      ) : null}

      {activeView === "comparison" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">Peer Matrix</p>
            <h3>{comparison.comparison}</h3>
            <div className="score-table">
              {comparison.score_matrix.map((row) => (
                <div className="score-row" key={row.ticker}>
                  <strong>{row.ticker}</strong>
                  <span>Cloud {row.scores.cloud_growth}</span>
                  <span>AI Capex {row.scores.ai_capex}</span>
                  <span>FCF {row.scores.fcf}</span>
                  <span>Moat {row.scores.moat}</span>
                  <span>Valuation {row.scores.valuation}</span>
                </div>
              ))}
            </div>
          </article>
        </div>
      ) : null}

      {activeView === "quality" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">Risk Auditor Agent</p>
            <h3>研究质量审计</h3>
            <p>
              Facts、Calculations、Assumptions、Interpretation、Risks、Open Questions 已分区输出。
            </p>
          </article>
          <article className="workspace-panel">
            <h3>Evidence</h3>
            <ul>
              {(nvidia.agent_report?.facts ?? []).map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>
          </article>
          <article className="workspace-panel">
            <h3>Quality Flags</h3>
            <ul>
              {(nvidia.quality_issues ?? []).map((issue) => (
                <li key={issue.category}>
                  {issue.severity}: {issue.message}
                </li>
              ))}
            </ul>
          </article>
        </div>
      ) : null}
    </section>
  );
}

function formatNumber(value: string | number) {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2
  }).format(numeric);
}
