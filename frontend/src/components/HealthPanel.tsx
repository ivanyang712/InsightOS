"use client";

import { useEffect, useState } from "react";

import { fetchHealth, type HealthResponse } from "@/src/lib/health";

type HealthState =
  | { status: "loading" }
  | { status: "ready"; data: HealthResponse }
  | { status: "error"; message: string };

export function HealthPanel() {
  const [state, setState] = useState<HealthState>({ status: "loading" });

  useEffect(() => {
    let active = true;

    fetchHealth()
      .then((data) => {
        if (active) {
          setState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            status: "error",
            message: error instanceof Error ? error.message : "Health check failed"
          });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (state.status === "loading") {
    return (
      <aside className="health-card">
        <div className="health-header">
          <p className="health-title">System health</p>
          <span className="badge warning">Checking</span>
        </div>
        <p className="lede">Connecting to the InsightOS API...</p>
      </aside>
    );
  }

  if (state.status === "error") {
    return (
      <aside className="health-card">
        <div className="health-header">
          <p className="health-title">System health</p>
          <span className="badge warning">Unavailable</span>
        </div>
        <p>{state.message}</p>
      </aside>
    );
  }

  const { data } = state;

  return (
    <aside className="health-card">
      <div className="health-header">
        <p className="health-title">System health</p>
        <span className={data.status === "ok" ? "badge" : "badge warning"}>{data.status}</span>
      </div>
      <ul className="health-list">
        <li className="health-row">
          <span>Service</span>
          <strong>{data.service}</strong>
        </li>
        <li className="health-row">
          <span>Environment</span>
          <strong>{data.environment}</strong>
        </li>
        <li className="health-row">
          <span>PostgreSQL</span>
          <strong>{data.checks.database ? "Connected" : "Unavailable"}</strong>
        </li>
        <li className="health-row">
          <span>Redis</span>
          <strong>{data.checks.redis ? "Connected" : "Unavailable"}</strong>
        </li>
      </ul>
    </aside>
  );
}
