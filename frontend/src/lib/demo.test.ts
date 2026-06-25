import assert from "node:assert/strict";
import { afterEach, describe, it, mock } from "node:test";

import { fetchDemoBundle } from "./demo";

describe("demo api helpers", () => {
  afterEach(() => {
    mock.restoreAll();
  });

  it("fetches the demo research bundle", async () => {
    mock.method(
      globalThis,
      "fetch",
      async (input: string | URL | Request) =>
        ({
          ok: true,
          json: async () => {
            const url = String(input);
            if (url.includes("nvidia")) {
              return { demo_notice: "demo", research_output: { executive_summary: "NVDA" } };
            }
            if (url.includes("semiconductor-equipment")) {
              return { demo_notice: "demo", industry: "Semi", cycle_indicators: [] };
            }
            return { demo_notice: "demo", comparison: "Cloud", score_matrix: [] };
          }
        }) as Response
    );

    const bundle = await fetchDemoBundle();

    assert.equal(bundle.source, "api");
    assert.equal(bundle.nvidia.research_output.executive_summary, "NVDA");
    assert.equal(bundle.industry.industry, "Semi");
    assert.equal(bundle.comparison.comparison, "Cloud");
  });

  it("falls back to synthetic data when the backend is unavailable", async () => {
    mock.method(globalThis, "fetch", async () => {
      throw new Error("offline");
    });

    const bundle = await fetchDemoBundle();

    assert.equal(bundle.source, "synthetic_fallback");
    assert.equal(bundle.nvidia.company?.ticker, "NVDA");
    assert.equal(bundle.comparison.score_matrix.length, 3);
  });
});
