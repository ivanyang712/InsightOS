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

export type ResearchStandardSection = {
  title: string;
  principle: string;
  checklist: string[];
};

export type DeepDiveSection = {
  title: string;
  summary: string;
  bullets: string[];
};

export type ScorecardItem = {
  label: string;
  score: number;
  rationale: string;
};

export type InvestmentCommitteeView = {
  conclusion: string;
  action: string;
  logic: string[];
  conditions_to_upgrade: string[];
  conditions_to_downgrade: string[];
  compliance_note: string;
};

export type SupplyChainBottleneck = {
  stage: string;
  bottleneck: string;
  expected_window: string;
  estimated_duration: string;
  severity: "low" | "medium" | "high" | "critical";
  involved_companies: string[];
  likely_beneficiaries: string[];
  investment_implication: string;
  watch_metrics: string[];
  evidence_date: string;
  confidence_score: number;
};

export type MarketPriceSummary = {
  status: "ok" | "unavailable" | string;
  ticker?: string;
  source_name?: string;
  source_url?: string;
  published_at?: string;
  retrieved_at?: string;
  source_hash?: string;
  confidence_score?: string | number;
  currency?: string;
  unit?: string;
  latest_date?: string;
  latest_close?: string | number;
  one_year_return?: string | number | null;
  trading_days?: number;
  data_status?: string;
  message?: string;
  note?: string;
};

export type HistoricalValidationEvent = {
  filing_type: string;
  filing_date: string;
  entry_date: string;
  entry_price: string | number;
  return_90d?: string | number | null;
  return_180d?: string | number | null;
  return_365d?: string | number | null;
};

export type HistoricalValidation = {
  status: "ok" | "unavailable" | string;
  methodology?: string;
  source_name?: string;
  source_url?: string;
  retrieved_at?: string;
  source_hash?: string;
  events: HistoricalValidationEvent[];
  summary: {
    sample_size?: number;
    median_180d_return?: string | number;
    positive_180d_hit_rate?: string | number;
  };
  verdict?: string;
  message?: string;
  limitations: string[];
};

export type InvestorDecision = {
  stance: string;
  action: string;
  not_personalized_advice: string;
  why_it_matters: string[];
  current_price_context: string;
  supporting_evidence: string[];
  decision_rules: string[];
  must_verify_next: string[];
  missing_evidence: string[];
  valuation_ready: boolean;
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
    exchange?: string;
    industry?: string;
    description?: string;
    sic?: string | null;
    sic_description?: string | null;
    archetype?: {
      name: string;
    };
  };
  ai_profile?: {
    categories: string[];
    relevance_score: number;
    reason: string;
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
  market_price?: MarketPriceSummary;
  historical_validation?: HistoricalValidation;
  investor_decision?: InvestorDecision;
  research_report: {
    facts: string[];
    calculations: string[];
    assumptions: string[];
    interpretation: string[];
    risks: string[];
    open_questions: string[];
  };
  research_standard?: ResearchStandardSection[];
  investment_committee?: InvestmentCommitteeView;
  business_analysis?: DeepDiveSection[];
  industry_analysis?: DeepDiveSection[];
  supply_chain_bottlenecks?: SupplyChainBottleneck[];
  quality_scorecard?: ScorecardItem[];
  quality_issues: QualityIssue[];
  confidence_score: string | number;
  sources: SourceSummary[];
  limitations: string[];
};

export type CompanyResearchBundle = {
  source: "api" | "synthetic_fallback";
  report: CompanyResearchResponse;
};
