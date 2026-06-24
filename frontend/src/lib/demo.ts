export type DemoResearchResponse = {
  demo_notice: string;
  research_output: {
    executive_summary: string;
    risks: string[];
    bull_base_bear: Record<string, string[]>;
    valuation: Record<string, unknown>;
  };
};

export type DemoIndustryResponse = {
  demo_notice: string;
  industry: string;
  cycle_indicators: string[];
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

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchDemoBundle() {
  const [nvidia, industry, comparison] = await Promise.all([
    fetchJson<DemoResearchResponse>("/api/demo/research/nvidia"),
    fetchJson<DemoIndustryResponse>("/api/demo/industry/semiconductor-equipment"),
    fetchJson<DemoComparisonResponse>("/api/demo/comparison/cloud-platforms")
  ]);
  return { nvidia, industry, comparison };
}
