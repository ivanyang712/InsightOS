import { describe, expect, it, vi } from "vitest";

import { fetchHealth, getApiBaseUrl } from "./health";

describe("health api helpers", () => {
  it("uses the configured API base url", () => {
    expect(getApiBaseUrl()).toBe("http://localhost:8000");
  });

  it("fetches the health response", async () => {
    const payload = {
      status: "ok",
      service: "InsightOS API",
      environment: "test",
      checks: {
        database: true,
        redis: true
      }
    };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => payload
      })
    );

    await expect(fetchHealth()).resolves.toEqual(payload);
  });
});
