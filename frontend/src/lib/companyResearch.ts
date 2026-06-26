export type CalculationResult = {
  metric: string;
  status: "ok" | "unavailable" | string;
  value: string | number | null;
  unit: string;
  fiscal_period: string;
  formula: string;
  message?: string | null;
};

export type NormalizedFact = {
  metric_name: string;
  value: string | number;
  unit: string;
  fiscal_period: string;
  fiscal_year: number | null;
  filed_at: string | null;
  source_url: string;
  source_hash: string;
};

export type FilingSummary = {
  accession_number: string;
  filing_type: string;
  filed_at: string;
  period_end_date: string | null;
  primary_document_url: string;
};

export type SourceSummary = {
  source_type: string;
  source_name: string;
  source_url: string;
  published_at: string;
  retrieved_at: string;
  source_hash: string;
  confidence_score: string | number;
};

export type QualityIssue = {
  severity: string;
  category: string;
  message: string;
  needs_human_review: boolean;
};

export type CompanyResearchResponse = {
  ticker: string;
  status: string;
  generated_at: string;
  data_source: string;
  company: {
    name: string;
    ticker: string;
    cik: string;
    sic?: string | null;
    sic_description?: string | null;
    archetype?: {
      name: string;
    };
  };
  latest_annual_period: string;
  filings: FilingSummary[];
  normalized_facts: NormalizedFact[];
  financial_quality: CalculationResult[];
  valuation: {
    status: string;
    dcf?: Record<string, Record<string, unknown>>;
    scenarios?: Record<string, Array<string | number>>;
    assumptions?: Record<string, string>;
  };
  research_report: {
    facts: string[];
    calculations: string[];
    assumptions: string[];
    interpretation: string[];
    risks: string[];
    open_questions: string[];
  };
  quality_issues: QualityIssue[];
  confidence_score: string | number;
  sources: SourceSummary[];
  limitations: string[];
};

export type CompanyResearchBundle = {
  source: "api" | "synthetic_fallback";
  report: CompanyResearchResponse;
};

const apiBaseUrl = () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchCompanyResearch(ticker: string): Promise<CompanyResearchBundle> {
  try {
    const normalizedTicker = ticker.trim().toUpperCase() || "AAPL";
    const response = await fetch(`${apiBaseUrl()}/api/research/company/${normalizedTicker}`, {
      cache: "no-store"
    });
    if (!response.ok) {
      throw new Error(`Research request failed with status ${response.status}`);
    }
    return { source: "api", report: (await response.json()) as CompanyResearchResponse };
  } catch {
    return { source: "synthetic_fallback", report: fallbackAppleResearch };
  }
}

export const fallbackAppleResearch: CompanyResearchResponse = {
  ticker: "AAPL",
  status: "completed",
  generated_at: "2026-06-26T00:00:00Z",
  data_source: "SEC EDGAR / SEC XBRL synthetic fixture",
  company: {
    name: "Apple Inc.",
    ticker: "AAPL",
    cik: "0000320193",
    sic: "3571",
    sic_description: "Electronic Computers",
    archetype: { name: "Consumer Goods" }
  },
  latest_annual_period: "FY2025",
  filings: [
    {
      accession_number: "0000320193-25-000079",
      filing_type: "10-K",
      filed_at: "2025-11-01",
      period_end_date: "2025-09-27",
      primary_document_url:
        "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm"
    }
  ],
  normalized_facts: [
    fact("revenues", 391035000000),
    fact("gross_profit", 181000000000),
    fact("operating_income", 123216000000),
    fact("net_income", 93736000000),
    fact("free_cash_flow", 106254000000)
  ],
  financial_quality: [
    metric("revenue_growth", "0.0202", "percent", "(current_revenue - previous_revenue) / previous_revenue"),
    metric("gross_margin", "0.4629", "ratio", "gross_profit / revenue"),
    metric("operating_margin", "0.3151", "ratio", "operating_income / revenue"),
    metric("net_margin", "0.2397", "ratio", "net_income / revenue"),
    metric("free_cash_flow_margin", "0.2717", "ratio", "free_cash_flow / revenue"),
    {
      metric: "inventory_turnover",
      status: "unavailable",
      value: null,
      unit: "n/a",
      fiscal_period: "FY2025-FY",
      formula: "cogs / average_inventory",
      message: "无法可靠计算：Missing cost_of_goods_sold or average_inventory."
    }
  ],
  valuation: {
    status: "completed",
    scenarios: {
      bear: [106254000000, 106254000000, 106254000000],
      base: [109441620000, 112724868600, 116106614658],
      bull: [112629240000, 119386994400, 126550214064]
    },
    assumptions: {
      bear_growth: "0% FCF CAGR for three years",
      base_growth: "3% FCF CAGR for three years",
      bull_growth: "6% FCF CAGR for three years",
      discount_rate: "10%",
      terminal_growth_rate: "2.5%"
    }
  },
  research_report: {
    facts: [
      "Apple Inc. is resolved from SEC company submissions.",
      "Financial facts are normalized from SEC XBRL companyfacts."
    ],
    calculations: [
      "gross_margin: gross_profit / revenue",
      "free_cash_flow_margin: free_cash_flow / revenue"
    ],
    assumptions: ["Assumptions are editable placeholders, not investment advice."],
    interpretation: [
      "The report is a deterministic first-pass research packet.",
      "Unavailable metrics are left unavailable rather than estimated."
    ],
    risks: [
      "Filings may not provide every operating metric required for this archetype.",
      "Valuation output is sensitive to placeholder growth and discount-rate assumptions."
    ],
    open_questions: [
      "Review the latest 10-K text for segment and supply-chain disclosures.",
      "Add market price data before producing PE, PS, or EV-based multiples."
    ]
  },
  quality_issues: [
    {
      severity: "medium",
      category: "calculation_gap",
      message: "Some operating metrics are unavailable from current normalized SEC facts.",
      needs_human_review: false
    }
  ],
  confidence_score: "0.8500",
  sources: [
    {
      source_type: "company_facts",
      source_name: "InsightOS Synthetic SEC Fixture",
      source_url: "internal://insightos/fixtures/aapl-companyfacts",
      published_at: "2026-06-26T00:00:00Z",
      retrieved_at: "2026-06-26T00:00:00Z",
      source_hash: "synthetic-fixture-hash",
      confidence_score: "0.8500"
    }
  ],
  limitations: [
    "No personalized buy/sell advice is generated.",
    "Market price data is not connected yet, so trading multiples are not produced."
  ]
};

function metric(
  name: string,
  value: string,
  unit: string,
  formula: string
): CalculationResult {
  return {
    metric: name,
    status: "ok",
    value,
    unit,
    fiscal_period: "FY2025-FY",
    formula
  };
}

function fact(metricName: string, value: number): NormalizedFact {
  return {
    metric_name: metricName,
    value,
    unit: "USD",
    fiscal_period: "FY2025-FY",
    fiscal_year: 2025,
    filed_at: "2025-11-01",
    source_url: "internal://insightos/fixtures/aapl-companyfacts",
    source_hash: "synthetic-fixture-hash"
  };
}
