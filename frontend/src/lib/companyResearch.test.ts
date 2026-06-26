import assert from "node:assert/strict";
import { afterEach, describe, it, mock } from "node:test";

import { fetchCompanyResearch } from "./companyResearch";

describe("company research api helpers", () => {
  afterEach(() => {
    mock.restoreAll();
  });

  it("fetches a single-company research packet", async () => {
    mock.method(
      globalThis,
      "fetch",
      async () =>
        ({
          ok: true,
          json: async () => ({
            ticker: "AAPL",
            status: "completed",
            company: { name: "Apple Inc.", ticker: "AAPL", cik: "0000320193" }
          })
        }) as Response
    );

    const bundle = await fetchCompanyResearch("aapl");

    assert.equal(bundle.source, "api");
    assert.equal(bundle.report.ticker, "AAPL");
    assert.equal(bundle.report.company.name, "Apple Inc.");
  });

  it("falls back when the research backend is unavailable", async () => {
    mock.method(globalThis, "fetch", async () => {
      throw new Error("offline");
    });

    const bundle = await fetchCompanyResearch("AAPL");

    assert.equal(bundle.source, "synthetic_fallback");
    assert.equal(bundle.report.company.cik, "0000320193");
    assert.ok(bundle.report.financial_quality.length > 0);
  });
});
