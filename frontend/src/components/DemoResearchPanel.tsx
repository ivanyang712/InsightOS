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
  const [state, setState] = useState<DemoState>({ status: "ready", data: fallbackDemoBundle });
  const [activeView, setActiveView] = useState<DemoView>("company");

  useEffect(() => {
    let active = true;
    Promise.race([fetchDemoBundle(), fallbackAfterDelay(fallbackDemoBundle)])
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
    return <section className="demo-panel">正在加载研究演示...</section>;
  }

  const { nvidia, industry, comparison } = state.data;
  const sourceLabel = state.data.source === "api" ? "后端 API" : "离线演示数据";

  return (
    <section className="demo-panel">
      <div className="panel-heading">
        <p className="eyebrow">研究工作流演示</p>
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
            <p className="eyebrow">公司研究 Agent</p>
            <h3>{nvidia.company?.name ?? "Nvidia"} 研究包</h3>
            <p>{nvidia.research_output.executive_summary}</p>
            <div className="metric-strip">
              <span>公司类型: {nvidia.company?.archetype?.name ?? "半导体"}</span>
              <span>可信度: {nvidia.agent_report?.confidence_score ?? "0.9000"}</span>
              <span>买卖建议语言: 已拦截</span>
            </div>
          </article>
          <article className="workspace-panel">
            <h3>风险</h3>
            <ul>
              {nvidia.research_output.risks.slice(0, 4).map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          </article>
          <article className="workspace-panel">
            <h3>待验证问题</h3>
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
            <p className="eyebrow">确定性计算服务</p>
            <h3>DCF / EV-Sales / PE 情景</h3>
            <div className="scenario-grid">
              {Object.entries(nvidia.research_output.bull_base_bear).map(([scenario, values]) => (
                <div className="scenario-card" key={scenario}>
                  <strong>{scenarioLabel(scenario)}</strong>
                  <span>{values.map(formatNumber).join(" / ")}</span>
                </div>
              ))}
            </div>
          </article>
          {(nvidia.research_output.financial_quality ?? []).slice(0, 4).map((metric) => (
            <article className="workspace-panel" key={metric.metric}>
              <h3>{metricLabel(metric.metric)}</h3>
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
            <p className="eyebrow">行业研究 Agent</p>
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
            <h3>周期指标</h3>
            <p>{industry.cycle_indicators.join(", ")}</p>
          </article>
          <article className="workspace-panel">
            <h3>跟踪指标</h3>
            <p>{industry.tracking_metrics.join(", ")}</p>
          </article>
        </div>
      ) : null}

      {activeView === "comparison" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">同业评分矩阵</p>
            <h3>{comparison.comparison}</h3>
            <div className="score-table">
              {comparison.score_matrix.map((row) => (
                <div className="score-row" key={row.ticker}>
                  <strong>{row.ticker}</strong>
                  <span>云业务增长 {row.scores.cloud_growth}</span>
                  <span>AI 资本开支 {row.scores.ai_capex}</span>
                  <span>自由现金流 {row.scores.fcf}</span>
                  <span>竞争壁垒 {row.scores.moat}</span>
                  <span>估值吸引力 {row.scores.valuation}</span>
                </div>
              ))}
            </div>
          </article>
        </div>
      ) : null}

      {activeView === "quality" ? (
        <div className="workspace-grid">
          <article className="workspace-panel wide">
            <p className="eyebrow">风险审计 Agent</p>
            <h3>研究质量审计</h3>
            <p>
              已验证事实、计算结果、关键假设、主观判断、风险和待验证问题已分区输出。
            </p>
          </article>
          <article className="workspace-panel">
            <h3>证据</h3>
            <ul>
              {(nvidia.agent_report?.facts ?? []).map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>
          </article>
          <article className="workspace-panel">
            <h3>质量标记</h3>
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

function fallbackAfterDelay<T>(value: T, ms = 2200): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);
  });
}

function metricLabel(metric: string) {
  const labels: Record<string, string> = {
    revenue_growth: "收入增长率",
    gross_margin: "毛利率",
    free_cash_flow_margin: "自由现金流率",
    inventory_turnover: "库存周转率"
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
