import { describe, expect, it } from "vitest";
import { computeBrandMetrics, computeCompetitorSov, type RunFacts } from "../src/worker/metrics";

const run = (over: Partial<RunFacts> = {}): RunFacts => ({
  brand_mentioned: false,
  brand_url_cited: false,
  brand_position: null,
  cited_brands: [],
  ...over,
});

describe("computeBrandMetrics", () => {
  it("SoV = mentioned / N (happy path, N=5)", () => {
    const runs = [
      run({ brand_mentioned: true, brand_position: 1, brand_url_cited: true }),
      run({ brand_mentioned: true, brand_position: 3 }),
      run({ brand_mentioned: true, brand_position: 2, brand_url_cited: true }),
      run(),
      run(),
    ];
    const m = computeBrandMetrics(runs);
    expect(m.n_runs).toBe(5);
    expect(m.sov).toBeCloseTo(3 / 5);
    expect(m.citation_rate).toBeCloseTo(2 / 5);
    expect(m.avg_position).toBeCloseTo((1 + 3 + 2) / 3);
  });

  it("never NaN when the brand is never cited (edge: SoV=0)", () => {
    const m = computeBrandMetrics([run(), run(), run()]);
    expect(m.sov).toBe(0);
    expect(m.citation_rate).toBe(0);
    expect(m.avg_position).toBeNull();
  });

  it("returns zeros for an empty run set", () => {
    const m = computeBrandMetrics([]);
    expect(m).toEqual({ n_runs: 0, sov: 0, citation_rate: 0, avg_position: null });
  });
});

describe("computeCompetitorSov", () => {
  const competitors = [
    { name: "The Dent", aliases: ["เดอะ เดนท์", "the dent"] },
    { name: "BIDC" },
  ];

  it("counts a Thai alias as the same competitor brand", () => {
    const runs: RunFacts[] = [
      run({ cited_brands: [{ name: "เดอะ เดนท์" }] }),
      run({ cited_brands: [{ name: "The Dent" }] }),
      run({ cited_brands: [{ name: "Some Other Clinic" }] }),
      run({ cited_brands: [{ name: "BIDC" }] }),
    ];
    const sov = computeCompetitorSov(competitors, runs);
    expect(sov["The Dent"]).toBeCloseTo(2 / 4);
    expect(sov["BIDC"]).toBeCloseTo(1 / 4);
  });

  it("returns 0 (not NaN) for every competitor on an empty run set", () => {
    const sov = computeCompetitorSov(competitors, []);
    expect(sov["The Dent"]).toBe(0);
    expect(sov["BIDC"]).toBe(0);
  });
});
