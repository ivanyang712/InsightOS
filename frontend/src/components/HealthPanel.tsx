"use client";

import { useEffect, useState } from "react";

import { fetchHealth, type HealthResponse } from "@/src/lib/health";

type HealthState =
  | { status: "loading" }
  | { status: "ready"; data: HealthResponse }
  | { status: "error"; message: string };

export function HealthPanel() {
  const [state, setState] = useState<HealthState>({
    status: "error",
    message: "后端 API 待连接"
  });

  useEffect(() => {
    let active = true;
    const fallbackTimer = setTimeout(() => {
      if (active) {
        setState({
            status: "error",
            message: "健康检查超时"
        });
      }
    }, 2200);

    fetchHealth()
      .then((data) => {
        if (active) {
          clearTimeout(fallbackTimer);
          setState({ status: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          clearTimeout(fallbackTimer);
          setState({
            status: "error",
            message: error instanceof Error ? translateHealthError(error.message) : "健康检查失败"
          });
        }
      });

    return () => {
      active = false;
      clearTimeout(fallbackTimer);
    };
  }, []);

  if (state.status === "loading") {
    return (
      <aside className="health-card">
        <div className="health-header">
          <p className="health-title">系统状态</p>
          <span className="badge warning">检查中</span>
        </div>
        <p className="lede">正在连接 InsightOS API...</p>
      </aside>
    );
  }

  if (state.status === "error") {
    return (
      <aside className="health-card">
        <div className="health-header">
          <p className="health-title">系统状态</p>
          <span className="badge warning">未连接</span>
        </div>
        <p className="health-message">
          后端 API 暂未连接，前端研究工作台会使用合成 fixture 继续展示。
        </p>
        <ul className="health-list">
          <li className="health-row">
            <span>API 状态</span>
            <strong>{state.message}</strong>
          </li>
          <li className="health-row">
            <span>前端演示</span>
            <strong>可用</strong>
          </li>
        </ul>
      </aside>
    );
  }

  const { data } = state;

  return (
    <aside className="health-card">
      <div className="health-header">
        <p className="health-title">系统状态</p>
        <span className={data.status === "ok" ? "badge" : "badge warning"}>
          {healthStatusLabel(data.status)}
        </span>
      </div>
      <ul className="health-list">
        <li className="health-row">
          <span>服务</span>
          <strong>{data.service}</strong>
        </li>
        <li className="health-row">
          <span>环境</span>
          <strong>{data.environment}</strong>
        </li>
        <li className="health-row">
          <span>PostgreSQL</span>
          <strong>{data.checks.database ? "已连接" : "未连接"}</strong>
        </li>
        <li className="health-row">
          <span>Redis</span>
          <strong>{data.checks.redis ? "已连接" : "未连接"}</strong>
        </li>
      </ul>
    </aside>
  );
}

function healthStatusLabel(status: HealthResponse["status"]) {
  if (status === "ok") {
    return "正常";
  }
  if (status === "degraded") {
    return "部分可用";
  }
  return "未连接";
}

function translateHealthError(message: string) {
  if (message.includes("timed out") || message.includes("abort")) {
    return "健康检查超时";
  }
  if (message.includes("failed")) {
    return "健康检查失败";
  }
  return message;
}
