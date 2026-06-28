export type HealthResponse = {
  status: "ok" | "degraded" | "unavailable";
  service: string;
  environment: string;
  checks: {
    database: boolean;
    redis: boolean;
  };
};

export function getApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function fetchHealth(): Promise<HealthResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 1800);
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}/health`, {
      cache: "no-store",
      signal: controller.signal
    });
  } finally {
    clearTimeout(timeout);
  }

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return normalizeHealthResponse(await response.json());
}

export function normalizeHealthResponse(payload: unknown): HealthResponse {
  const record = isRecord(payload) ? payload : {};
  const checks = isRecord(record.checks) ? record.checks : {};

  return {
    status:
      record.status === "ok" || record.status === "degraded" ? record.status : "unavailable",
    service: typeof record.service === "string" ? record.service : "InsightOS API",
    environment: typeof record.environment === "string" ? record.environment : "unknown",
    checks: {
      database: checks.database === true,
      redis: checks.redis === true
    }
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
