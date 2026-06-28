export type DemoResearchResponse = {
  demo_notice: string;
  company?: {
    name: string;
    ticker: string;
    archetype?: {
      name: string;
    };
  };
  research_output: {
    executive_summary: string;
    financial_quality?: Array<{
      metric: string;
      status: string;
      value: string | number | null;
      unit: string;
      formula: string;
      message?: string | null;
    }>;
    risks: string[];
    catalysts?: string[];
    bull_base_bear: Record<string, Array<string | number>>;
    valuation: Record<string, unknown>;
    key_assumptions?: Record<string, string>;
    sources_and_confidence?: string[];
  };
  agent_report?: {
    facts: string[];
    calculations: string[];
    risks: string[];
    open_questions: string[];
    confidence_score: string | number;
  };
  quality_issues?: Array<{
    severity: string;
    category: string;
    message: string;
    needs_human_review: boolean;
  }>;
};

export type DemoIndustryResponse = {
  demo_notice: string;
  industry: string;
  value_chain_map?: Record<string, string[]>;
  market_size_growth_drivers?: string[];
  competitive_landscape?: string[];
  cycle_indicators: string[];
  three_year_risks_catalysts?: {
    risks: string[];
    catalysts: string[];
  };
  tracking_metrics: string[];
};

export type DemoComparisonResponse = {
  demo_notice: string;
  comparison: string;
  score_matrix: Array<{
    ticker: string;
    scores: Record<string, number>;
  }>;
};

export type DemoBundle = {
  nvidia: DemoResearchResponse;
  industry: DemoIndustryResponse;
  comparison: DemoComparisonResponse;
  source: "api" | "synthetic_fallback";
};

export const fallbackDemoBundle: DemoBundle = {
  source: "synthetic_fallback",
  nvidia: {
    demo_notice:
      "当前为离线演示数据，仅用于验证产品流程；不是生产市场数据，也不构成投资建议。",
    company: {
      name: "Nvidia",
      ticker: "NVDA",
      archetype: { name: "Semiconductor" }
    },
    research_output: {
      executive_summary:
        "演示结论：AI 需求可持续性取决于云厂商资本开支广度、毛利结构和客户集中度证据。",
      financial_quality: [
        {
          metric: "revenue_growth",
          status: "ok",
          value: "0.4118",
          unit: "percent",
          formula: "(current_revenue - previous_revenue) / previous_revenue"
        },
        {
          metric: "gross_margin",
          status: "ok",
          value: "0.7500",
          unit: "ratio",
          formula: "gross_profit / revenue"
        },
        {
          metric: "free_cash_flow_margin",
          status: "ok",
          value: "0.4833",
          unit: "ratio",
          formula: "free_cash_flow / revenue"
        },
        {
          metric: "inventory_turnover",
          status: "unavailable",
          value: null,
          unit: "n/a",
          formula: "cogs / average_inventory",
          message: "无法可靠计算：缺少营业成本或平均库存。"
        }
      ],
      risks: [
        "AI 资本开支消化风险",
        "毛利率正常化风险",
        "云厂商客户集中度风险",
        "出口管制与供应链风险"
      ],
      catalysts: ["新平台周期", "企业推理场景扩散", "供应能力扩张"],
      bull_base_bear: {
        bear: [60900, 63945, 67142.25],
        base: [67280, 78044.8, 90531.968],
        bull: [73080, 92080.8, 116021.808]
      },
      valuation: {
        dcf: "由确定性 Python 服务生成 DCF 乐观/基准/悲观情景。",
        ev_sales: "EV/Sales 倍数视角",
        pe: "PE 倍数视角"
      },
      key_assumptions: {
        bear_growth: "悲观情景：三年自由现金流 CAGR 5%",
        base_growth: "基准情景：三年自由现金流 CAGR 16%",
        bull_growth: "乐观情景：三年自由现金流 CAGR 26%"
      },
      sources_and_confidence: [
        "InsightOS Synthetic Nvidia Fixture | internal://insightos/demo/nvidia | published=2026-06-23 | retrieved=2026-06-23T00:00:00Z | confidence=0.9000"
      ]
    },
    agent_report: {
      facts: [
        "演示数据表明 AI 加速器需求仍强，但依赖云厂商资本开支持续性。",
        "演示研究将数据中心收入质量与一次性库存补货区分开。"
      ],
      calculations: ["gross_profit / revenue"],
      risks: ["客户集中度和毛利率正常化需要单独做证据审计。"],
      open_questions: [
        "最新申报文件中有哪些客户集中度披露？"
      ],
      confidence_score: "0.9000"
    },
    quality_issues: [
      {
        severity: "medium",
        category: "calculation_gap",
        message: "缺少营运资本输入，因此库存周转率无法可靠计算。",
        needs_human_review: false
      }
    ]
  },
  industry: {
    demo_notice:
      "当前为离线演示数据，仅用于验证产品流程；不是生产市场数据，也不构成投资建议。",
    industry: "Global Semiconductor Equipment",
    value_chain_map: {
      upstream: ["精密零部件", "光学系统", "真空系统", "特种材料"],
      midstream: ["光刻", "刻蚀", "薄膜沉积", "量测", "检测"],
      downstream: ["晶圆代工", "存储厂商", "IDM", "先进封装"]
    },
    market_size_growth_drivers: [
      "先进制程资本开支",
      "AI 加速器需求",
      "存储技术迭代",
      "区域晶圆厂本地化"
    ],
    competitive_landscape: [
      "技术壁垒高",
      "存量设备服务收入稳定",
      "出口管制导致市场分层"
    ],
    cycle_indicators: [
      "订单出货比",
      "晶圆厂设备支出",
      "存储价格",
      "晶圆代工产能利用率"
    ],
    three_year_risks_catalysts: {
      risks: ["资本开支消化", "出口限制", "存储下行周期"],
      catalysts: ["先进封装", "HBM 需求", "晶圆厂本地化补贴"]
    },
    tracking_metrics: ["订单出货比", "交付周期", "晶圆代工产能利用率", "存储 ASP"]
  },
  comparison: {
    demo_notice:
      "当前为离线演示数据，仅用于验证产品流程；不是生产市场数据，也不构成投资建议。",
    comparison: "Microsoft / Google / Amazon 对比",
    score_matrix: [
      {
        ticker: "MSFT",
        scores: { cloud_growth: 82, ai_capex: 70, fcf: 86, valuation: 60, moat: 88 }
      },
      {
        ticker: "GOOGL",
        scores: { cloud_growth: 75, ai_capex: 76, fcf: 90, valuation: 68, moat: 86 }
      },
      {
        ticker: "AMZN",
        scores: { cloud_growth: 78, ai_capex: 82, fcf: 74, valuation: 62, moat: 84 }
      }
    ]
  }
};

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function fetchJson<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 1800);
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}${path}`, {
      cache: "no-store",
      signal: controller.signal
    });
  } finally {
    clearTimeout(timeout);
  }
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchDemoBundle(): Promise<DemoBundle> {
  try {
    const [nvidia, industry, comparison] = await Promise.all([
      fetchJson<DemoResearchResponse>("/api/demo/research/nvidia"),
      fetchJson<DemoIndustryResponse>("/api/demo/industry/semiconductor-equipment"),
      fetchJson<DemoComparisonResponse>("/api/demo/comparison/cloud-platforms")
    ]);
    return { nvidia, industry, comparison, source: "api" };
  } catch {
    return fallbackDemoBundle;
  }
}
