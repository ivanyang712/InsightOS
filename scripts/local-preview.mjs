import { createServer } from "node:http";

const port = Number(process.env.PORT ?? 3000);
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const html = `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>InsightOS</title>
    <style>
      :root {
        color-scheme: light;
        --background: #f7f8f5;
        --foreground: #17201a;
        --muted: #5c675f;
        --panel: #ffffff;
        --border: #d9ded7;
        --accent: #176c5f;
        --accent-soft: #e1f2ee;
        --warning: #9a5b12;
      }
      * { box-sizing: border-box; }
      body {
        min-height: 100vh;
        margin: 0;
        background: var(--background);
        color: var(--foreground);
        font-family: Arial, Helvetica, sans-serif;
      }
      .shell { min-height: 100vh; padding: 64px; }
      .hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 420px;
        gap: 48px;
        align-items: center;
        max-width: 1120px;
        min-height: calc(100vh - 128px);
        margin: 0 auto;
      }
      .eyebrow {
        margin: 0 0 16px;
        color: var(--accent);
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0;
        text-transform: uppercase;
      }
      h1 {
        max-width: 760px;
        margin: 0;
        font-size: clamp(42px, 7vw, 84px);
        line-height: 0.98;
        letter-spacing: 0;
      }
      .lede {
        max-width: 680px;
        margin: 24px 0 0;
        color: var(--muted);
        font-size: 20px;
        line-height: 1.6;
      }
      .health-card {
        width: 100%;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--panel);
        padding: 24px;
        box-shadow: 0 20px 60px rgb(23 32 26 / 8%);
      }
      .health-header {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: center;
        margin-bottom: 20px;
      }
      .health-title {
        margin: 0;
        font-size: 18px;
        font-weight: 700;
      }
      .badge {
        display: inline-flex;
        align-items: center;
        min-height: 28px;
        border-radius: 999px;
        padding: 4px 10px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 13px;
        font-weight: 700;
      }
      .badge.warning { background: #fff3db; color: var(--warning); }
      .health-list {
        display: grid;
        gap: 12px;
        margin: 0;
        padding: 0;
        list-style: none;
      }
      .health-row {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        border-top: 1px solid var(--border);
        padding-top: 12px;
        color: var(--muted);
      }
      .health-row strong { color: var(--foreground); }
      .demo-panel {
        max-width: 1120px;
        margin: 0 auto 64px;
        border-top: 1px solid var(--border);
        padding-top: 36px;
      }
      .research-panel {
        max-width: 1120px;
        margin: 0 auto 64px;
        border-top: 1px solid var(--border);
        padding-top: 36px;
      }
      .ticker-form {
        display: grid;
        grid-template-columns: auto minmax(140px, 220px) auto;
        align-items: center;
        gap: 10px;
        margin: 0 0 20px;
      }
      .ticker-form input {
        min-height: 42px;
        border: 1px solid var(--border);
        border-radius: 8px;
        font: inherit;
        padding: 0 12px;
        text-transform: uppercase;
      }
      .ticker-form button {
        min-height: 42px;
        border: 0;
        border-radius: 8px;
        background: var(--accent);
        color: #fff;
        cursor: pointer;
        font: inherit;
        font-weight: 700;
        padding: 0 16px;
      }
      .panel-heading { max-width: 760px; margin-bottom: 24px; }
      .panel-heading h2 { margin: 0; font-size: 32px; letter-spacing: 0; }
      .panel-heading p { color: var(--muted); line-height: 1.6; }
      .demo-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
      }
      .demo-grid article {
        min-height: 260px;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--panel);
        padding: 20px;
      }
      .demo-grid h3 { margin: 0 0 12px; font-size: 18px; }
      .demo-grid p, .demo-grid li { color: var(--muted); line-height: 1.5; }
      .score-row {
        display: grid;
        gap: 4px;
        border-top: 1px solid var(--border);
        padding-top: 10px;
        color: var(--muted);
      }
      .score-row strong { color: var(--foreground); }
      @media (max-width: 820px) {
        .shell { padding: 32px 20px; }
        .hero { grid-template-columns: 1fr; min-height: auto; }
        .ticker-form { grid-template-columns: 1fr; }
        .demo-grid { grid-template-columns: 1fr; }
        h1 { font-size: 44px; }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <div>
          <p class="eyebrow">InsightOS MVP</p>
          <h1>可验证的 AI 投资研究工作台</h1>
          <p class="lede">当前骨架已包含 Next.js 前端、FastAPI 后端、PostgreSQL、Redis 和 Docker Compose。</p>
        </div>
        <aside class="health-card">
          <div class="health-header">
            <p class="health-title">System health</p>
            <span id="status" class="badge warning">Checking</span>
          </div>
          <ul class="health-list">
            <li class="health-row"><span>Service</span><strong id="service">Connecting...</strong></li>
            <li class="health-row"><span>Environment</span><strong id="environment">-</strong></li>
            <li class="health-row"><span>PostgreSQL</span><strong id="database">-</strong></li>
            <li class="health-row"><span>Redis</span><strong id="redis">-</strong></li>
          </ul>
        </aside>
      </section>
      <section class="research-panel">
        <div class="panel-heading">
          <p class="eyebrow">Single Stock Research</p>
          <h2>单只股票研究主链路</h2>
          <p>输入 ticker 后，系统会尝试调用后端 SEC/XBRL 研究 API；后端不可用时展示 AAPL synthetic fallback。</p>
        </div>
        <form class="ticker-form" id="ticker-form">
          <label for="ticker">Ticker</label>
          <input id="ticker" value="AAPL" />
          <button type="submit">Run Research</button>
        </form>
        <div class="demo-grid">
          <article>
            <h3 id="stock-title">Apple Inc. (AAPL)</h3>
            <p id="stock-summary">Loading single-stock research packet...</p>
            <ul id="stock-facts"></ul>
          </article>
          <article>
            <h3>Financial Metrics</h3>
            <div id="stock-metrics"></div>
          </article>
          <article>
            <h3>Evidence Chain</h3>
            <div id="stock-sources"></div>
          </article>
        </div>
      </section>
      <section class="demo-panel">
        <div class="panel-heading">
          <p class="eyebrow">Research Workflow Demo</p>
          <h2>InsightOS 投研工作台体验</h2>
          <p id="demo-notice">Loading demo research workflow...</p>
        </div>
        <div class="demo-grid">
          <article>
            <h3>Nvidia Company Research</h3>
            <p id="nvidia-summary">Loading...</p>
            <ul id="nvidia-risks"></ul>
          </article>
          <article>
            <h3 id="industry-title">Industry Research</h3>
            <p id="industry-cycle">Loading...</p>
            <p id="industry-tracking"></p>
          </article>
          <article>
            <h3 id="comparison-title">Company Comparison</h3>
            <div id="comparison-scores"></div>
          </article>
        </div>
      </section>
    </main>
    <script>
      const apiBaseUrl = ${JSON.stringify(apiBaseUrl)};
      fetch(apiBaseUrl + "/health")
        .then((response) => response.json())
        .then((data) => {
          const status = document.getElementById("status");
          status.textContent = data.status;
          status.className = data.status === "ok" ? "badge" : "badge warning";
          document.getElementById("service").textContent = data.service;
          document.getElementById("environment").textContent = data.environment;
          document.getElementById("database").textContent = data.checks.database ? "Connected" : "Unavailable";
          document.getElementById("redis").textContent = data.checks.redis ? "Connected" : "Unavailable";
        })
        .catch((error) => {
          document.getElementById("status").textContent = "Unavailable";
          document.getElementById("service").textContent = error.message;
        });

      const stockFallback = {
        ticker: "AAPL",
        company: { name: "Apple Inc.", cik: "0000320193" },
        latest_annual_period: "FY2025",
        research_report: {
          facts: [
            "Apple Inc. is resolved from SEC company submissions.",
            "Financial facts are normalized from SEC XBRL companyfacts."
          ]
        },
        financial_quality: [
          { metric: "revenue_growth", status: "ok", value: "0.0202", formula: "(current_revenue - previous_revenue) / previous_revenue" },
          { metric: "gross_margin", status: "ok", value: "0.4629", formula: "gross_profit / revenue" },
          { metric: "free_cash_flow_margin", status: "ok", value: "0.2717", formula: "free_cash_flow / revenue" }
        ],
        sources: [
          { source_name: "InsightOS Synthetic SEC Fixture", confidence_score: "0.8500" }
        ]
      };
      function renderStock(report, sourceLabel) {
        document.getElementById("stock-title").textContent = report.company.name + " (" + report.ticker + ")";
        document.getElementById("stock-summary").textContent = "Source: " + sourceLabel + " · " + report.latest_annual_period + " · CIK " + report.company.cik;
        document.getElementById("stock-facts").innerHTML = report.research_report.facts
          .map((fact) => "<li>" + fact + "</li>")
          .join("");
        document.getElementById("stock-metrics").innerHTML = report.financial_quality
          .slice(0, 4)
          .map((metric) => "<div class='score-row'><strong>" + metric.metric + "</strong><span>" + (metric.value ?? "无法可靠计算") + "</span><span>" + metric.formula + "</span></div>")
          .join("");
        document.getElementById("stock-sources").innerHTML = report.sources
          .map((source) => "<div class='score-row'><strong>" + source.source_name + "</strong><span>confidence " + source.confidence_score + "</span></div>")
          .join("");
      }
      function loadStock(ticker) {
        fetch(apiBaseUrl + "/api/research/company/" + encodeURIComponent(ticker))
          .then((response) => {
            if (!response.ok) throw new Error("Research API unavailable");
            return response.json();
          })
          .then((report) => renderStock(report, "Live API"))
          .catch(() => renderStock(stockFallback, "Synthetic fallback"));
      }
      document.getElementById("ticker-form").addEventListener("submit", (event) => {
        event.preventDefault();
        loadStock(document.getElementById("ticker").value || "AAPL");
      });
      loadStock("AAPL");

      Promise.all([
        fetch(apiBaseUrl + "/api/demo/research/nvidia").then((response) => response.json()),
        fetch(apiBaseUrl + "/api/demo/industry/semiconductor-equipment").then((response) => response.json()),
        fetch(apiBaseUrl + "/api/demo/comparison/cloud-platforms").then((response) => response.json())
      ])
        .then(([nvidia, industry, comparison]) => {
          document.getElementById("demo-notice").textContent = nvidia.demo_notice;
          document.getElementById("nvidia-summary").textContent = nvidia.research_output.executive_summary;
          document.getElementById("nvidia-risks").innerHTML = nvidia.research_output.risks
            .slice(0, 4)
            .map((risk) => "<li>" + risk + "</li>")
            .join("");
          document.getElementById("industry-title").textContent = industry.industry;
          document.getElementById("industry-cycle").textContent = "Cycle indicators: " + industry.cycle_indicators.join(", ");
          document.getElementById("industry-tracking").textContent = "Tracking metrics: " + industry.tracking_metrics.join(", ");
          document.getElementById("comparison-title").textContent = comparison.comparison;
          document.getElementById("comparison-scores").innerHTML = comparison.score_matrix
            .map((row) => "<div class='score-row'><strong>" + row.ticker + "</strong><span>Moat " + row.scores.moat + "</span><span>FCF " + row.scores.fcf + "</span><span>Valuation " + row.scores.valuation + "</span></div>")
            .join("");
        })
        .catch((error) => {
          const fallback = {
            nvidia: {
              demo_notice: "Synthetic demo data for workflow testing only. Backend API unavailable.",
              research_output: {
                executive_summary: "Demo workflow: AI demand durability depends on capex breadth, margin mix, and customer concentration evidence.",
                risks: [
                  "AI capex digestion risk",
                  "gross margin normalization risk",
                  "hyperscaler customer concentration risk",
                  "export-control and supply-chain risk"
                ]
              }
            },
            industry: {
              industry: "Global Semiconductor Equipment",
              cycle_indicators: ["book-to-bill", "wafer fab equipment spend", "memory pricing", "foundry utilization"],
              tracking_metrics: ["lead times", "foundry utilization", "memory ASP", "capex guidance"]
            },
            comparison: {
              comparison: "Microsoft vs Google vs Amazon",
              score_matrix: [
                { ticker: "MSFT", scores: { moat: 88, fcf: 86, valuation: 60 } },
                { ticker: "GOOGL", scores: { moat: 86, fcf: 90, valuation: 68 } },
                { ticker: "AMZN", scores: { moat: 84, fcf: 74, valuation: 62 } }
              ]
            }
          };
          document.getElementById("demo-notice").textContent = fallback.nvidia.demo_notice + " " + error.message;
          document.getElementById("nvidia-summary").textContent = fallback.nvidia.research_output.executive_summary;
          document.getElementById("nvidia-risks").innerHTML = fallback.nvidia.research_output.risks
            .map((risk) => "<li>" + risk + "</li>")
            .join("");
          document.getElementById("industry-title").textContent = fallback.industry.industry;
          document.getElementById("industry-cycle").textContent = "Cycle indicators: " + fallback.industry.cycle_indicators.join(", ");
          document.getElementById("industry-tracking").textContent = "Tracking metrics: " + fallback.industry.tracking_metrics.join(", ");
          document.getElementById("comparison-title").textContent = fallback.comparison.comparison;
          document.getElementById("comparison-scores").innerHTML = fallback.comparison.score_matrix
            .map((row) => "<div class='score-row'><strong>" + row.ticker + "</strong><span>Moat " + row.scores.moat + "</span><span>FCF " + row.scores.fcf + "</span><span>Valuation " + row.scores.valuation + "</span></div>")
            .join("");
        });
    </script>
  </body>
</html>`;

createServer((request, response) => {
  if (request.url === "/" || request.url?.startsWith("/?")) {
    response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    response.end(html);
    return;
  }

  response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
  response.end("Not found");
}).listen(port, () => {
  console.log(`InsightOS local preview: http://localhost:${port}`);
});
