"use client";

import { useEffect, useState } from "react";

import { fetchDemoBundle } from "@/src/lib/demo";

type DemoBundle = Awaited<ReturnType<typeof fetchDemoBundle>>;

type DemoState =
  | { status: "loading" }
  | { status: "ready"; data: DemoBundle }
  | { status: "error"; message: string };

export function DemoResearchPanel() {
  const [state, setState] = useState<DemoState>({ status: "loading" });

  useEffect(() => {
    let active = true;
    fetchDemoBundle()
      .then((data) => {
        if (active) {
          setState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            status: "error",
            message: error instanceof Error ? error.message : "Demo request failed"
          });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (state.status === "loading") {
    return <section className="demo-panel">Loading research demo...</section>;
  }

  if (state.status === "error") {
    return <section className="demo-panel warning-panel">{state.message}</section>;
  }

  const { nvidia, industry, comparison } = state.data;

  return (
    <section className="demo-panel">
      <div className="panel-heading">
        <p className="eyebrow">Research Workflow Demo</p>
        <h2>Nvidia、半导体设备产业、云平台对比</h2>
        <p>{nvidia.demo_notice}</p>
      </div>

      <div className="demo-grid">
        <article>
          <h3>Nvidia Company Research</h3>
          <p>{nvidia.research_output.executive_summary}</p>
          <ul>
            {nvidia.research_output.risks.slice(0, 4).map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </article>

        <article>
          <h3>{industry.industry}</h3>
          <p>Cycle indicators: {industry.cycle_indicators.join(", ")}</p>
          <p>Tracking metrics: {industry.tracking_metrics.join(", ")}</p>
        </article>

        <article>
          <h3>{comparison.comparison}</h3>
          <div className="score-table">
            {comparison.score_matrix.map((row) => (
              <div className="score-row" key={row.ticker}>
                <strong>{row.ticker}</strong>
                <span>Moat {row.scores.moat}</span>
                <span>FCF {row.scores.fcf}</span>
                <span>Valuation {row.scores.valuation}</span>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}
