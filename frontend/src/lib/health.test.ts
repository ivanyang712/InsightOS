import assert from "node:assert/strict";
import { afterEach, describe, it, mock } from "node:test";

import { fetchHealth, getApiBaseUrl, normalizeHealthResponse } from "./health";

describe("health api helpers", () => {
  afterEach(() => {
    mock.restoreAll();
  });

  it("uses the configured API base url", () => {
    assert.equal(getApiBaseUrl(), "http://localhost:8000");
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

    mock.method(
      globalThis,
      "fetch",
      async () =>
        ({
        ok: true,
        json: async () => payload
        }) as Response
    );

    assert.deepEqual(await fetchHealth(), payload);
  });

  it("normalizes partial health responses", () => {
    assert.deepEqual(normalizeHealthResponse({ detail: "Not Found" }), {
      status: "unavailable",
      service: "InsightOS API",
      environment: "unknown",
      checks: {
        database: false,
        redis: false
      }
    });
  });
});
