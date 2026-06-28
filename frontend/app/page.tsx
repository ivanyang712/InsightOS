import { SingleStockResearchPanel } from "@/src/components/SingleStockResearchPanel";
import { companyNameAliases } from "@/src/lib/aiCompanyCatalog";
import type { CompanyResearchBundle } from "@/src/lib/researchTypes";

type HomeProps = {
  searchParams?: Promise<{
    ticker?: string | string[];
    view?: string | string[];
  }>;
};

export default async function Home({ searchParams }: HomeProps) {
  const params = await searchParams;
  const tickerParam = params?.ticker;
  const viewParam = params?.view;
  const initialTicker = normalizeTicker(Array.isArray(tickerParam) ? tickerParam[0] : tickerParam);
  const initialView = normalizeView(Array.isArray(viewParam) ? viewParam[0] : viewParam);
  const initialResearch = await loadInitialResearch(initialTicker);
  const hasOnlineResearch = Boolean(initialResearch.data);

  return (
    <main className="landing-page">
      <section className="landing-hero">
        <div className="hero-shade" />
        <nav className="top-nav" aria-label="InsightOS navigation">
          <strong>InsightOS</strong>
          <div>
            <a href="#single-stock">公司研究</a>
            <a href="#workflow">证据链</a>
          </div>
        </nav>

        <div className="hero-content">
          <p className="eyebrow hero-eyebrow">AI 投资研究系统</p>
          <h1>
            把投研结论拆回<span className="hero-term">事实</span>、
            <span className="hero-term">公式</span>、<span className="hero-term">假设</span>
            和<span className="hero-term">证据</span>
          </h1>
          <p className="lede">
            InsightOS 面向美股公司与美国宏观数据，生成可复算、可审计、可追溯的研究工作底稿。
            它不做自动交易，也不输出个性化买卖建议。
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="#single-stock">开始单股研究</a>
            <a className="secondary-action" href="#workflow">查看研究链路</a>
          </div>
          <dl className="hero-proof">
            <div>
              <dt>16</dt>
              <dd>证据链数据模型</dd>
            </div>
            <div>
              <dt>3</dt>
              <dd>估值情景</dd>
            </div>
            <div>
              <dt>0</dt>
              <dd>交易执行</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="status-band">
        <aside className="health-card">
          <div className="health-header">
            <p className="health-title">在线数据状态</p>
            <span className={hasOnlineResearch ? "badge" : "badge warning"}>
              {hasOnlineResearch ? "已连接 SEC" : "未连接"}
            </span>
          </div>
          <p className="health-message">
            {hasOnlineResearch
              ? `${initialTicker} 已从 SEC EDGAR / XBRL 获取在线公司申报与财务事实。页面只展示在线接口返回的研究结果。`
              : initialResearch.error?.message ?? "在线研究接口暂不可用。"}
          </p>
        </aside>
      </section>

      <section className="workflow-section" id="workflow">
        <div className="panel-heading">
          <p className="eyebrow">研究链路</p>
          <h2>从 ticker 到研究报告，每一步都留痕</h2>
          <p>
            第一版优先跑通单只股票：公司识别、数据来源、标准化事实、确定性计算、情景估值、
            质量审计和前端可读报告。
          </p>
        </div>
        <div className="workflow-grid">
          <article>
            <span>01</span>
            <h3>读取公司与申报</h3>
            <p>通过 ticker 映射 CIK，进入 SEC profile、filings 和 XBRL facts 的 raw layer。</p>
          </article>
          <article>
            <span>02</span>
            <h3>标准化财务事实</h3>
            <p>保留 source url、retrieved_at、source_hash、期间、币种与置信度。</p>
          </article>
          <article>
            <span>03</span>
            <h3>复算指标与估值</h3>
            <p>财务质量、DCF 与 Bull/Base/Bear 情景由 Python 服务计算，不交给 LLM 猜数。</p>
          </article>
          <article>
            <span>04</span>
            <h3>输出可审计结论</h3>
            <p>报告区分已验证事实、计算结果、关键假设、主观判断、风险和待验证问题。</p>
          </article>
        </div>
      </section>

      <SingleStockResearchPanel
        initialError={initialResearch.error}
        initialResearch={initialResearch.data}
        initialTicker={initialTicker}
        initialView={initialView}
      />
    </main>
  );
}

async function loadInitialResearch(ticker: string): Promise<{
  data?: CompanyResearchBundle;
  error?: {
    ticker: string;
    message: string;
  };
}> {
  const backendBaseUrl = process.env.BACKEND_API_BASE_URL ?? "http://127.0.0.1:8001";
  try {
    const response = await fetch(`${backendBaseUrl}/api/research/company/${ticker}`, {
      cache: "no-store",
      headers: {
        accept: "application/json"
      }
    });
    if (!response.ok) {
      let message = `在线研究接口返回 ${response.status}`;
      try {
        const payload = (await response.json()) as { detail?: string };
        message = payload.detail ?? message;
      } catch {
        // Keep the status message when the backend returns non-JSON.
      }
      return { error: { ticker, message } };
    }
    return { data: { source: "api", report: (await response.json()) as CompanyResearchBundle["report"] } };
  } catch (error) {
    return {
      error: {
        ticker,
        message: error instanceof Error ? error.message : "在线研究接口不可用"
      }
    };
  }
}

function normalizeTicker(ticker?: string): string {
  const normalized = ticker?.trim().toUpperCase() ?? "";
  return companyNameAliases[normalized] ?? (normalized || "NVDA");
}

function normalizeView(view?: string): string {
  const allowedViews = new Set([
    "committee",
    "business",
    "industry",
    "bottlenecks",
    "validation",
    "metrics",
    "valuation",
    "risk",
    "evidence"
  ]);
  return view && allowedViews.has(view) ? view : "committee";
}
