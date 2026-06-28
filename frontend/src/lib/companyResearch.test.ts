import assert from "node:assert/strict";
import { afterEach, describe, it, mock } from "node:test";

import {
  fetchCompanyResearch,
  getFallbackCompanyResearch,
  supportedFallbackTickers
} from "./companyResearch";

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

  it("does not substitute synthetic data when the research backend is unavailable", async () => {
    mock.method(globalThis, "fetch", async () => {
      throw new Error("offline");
    });

    await assert.rejects(fetchCompanyResearch("NVDA"), /offline|aborted|fetch/i);
  });

  it("lists the supported first-phase AI research tickers", () => {
    assert.deepEqual(supportedFallbackTickers, [
      "NVDA",
      "MSFT",
      "GOOGL",
      "AMZN",
      "META",
      "AMD",
      "AVGO",
      "TSM",
      "ASML",
      "PLTR"
    ]);
  });

  it("maps common company names to BRD ticker aliases", () => {
    const report = getFallbackCompanyResearch("Palantir");

    assert.equal(report.ticker, "PLTR");
    assert.equal(report.company.name, "Palantir Technologies Inc.");
    assert.ok(report.ai_profile?.categories.includes("AI 软件"));
  });

  it("returns a clear unavailable packet for unsupported local research packets", () => {
    const report = getFallbackCompanyResearch("TSLA");

    assert.equal(report.ticker, "TSLA");
    assert.equal(report.status, "unsupported");
    assert.equal(report.financial_quality[0].status, "unavailable");
    assert.equal(report.quality_issues[0].category, "missing_evidence");
  });

  it("includes an investment committee view for supported research packets", () => {
    const report = getFallbackCompanyResearch("NVDA");

    assert.ok(report.investment_committee?.conclusion.includes("高优先级"));
    assert.ok(report.investment_committee?.conditions_to_downgrade.length);
    assert.ok(report.business_analysis?.some((section) => section.title === "护城河与反证"));
    assert.ok(report.research_standard?.some((section) => section.title === "好价格"));
  });

  it("maps Nvidia supply chain bottlenecks with timing and beneficiaries", () => {
    const report = getFallbackCompanyResearch("NVDA");

    assert.ok(report.supply_chain_bottlenecks?.some((item) => item.stage.includes("HBM")));
    assert.ok(report.supply_chain_bottlenecks?.some((item) => item.likely_beneficiaries.includes("TSMC")));
    assert.ok(report.supply_chain_bottlenecks?.every((item) => item.expected_window.length > 0));
    assert.ok(report.supply_chain_bottlenecks?.every((item) => item.watch_metrics.length >= 3));
  });
});
