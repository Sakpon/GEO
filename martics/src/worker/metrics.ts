import type { Competitor } from "./types";

/** Minimal shape the metric math needs from a run. */
export interface RunFacts {
  brand_mentioned: boolean;
  brand_url_cited: boolean;
  brand_position: number | null;
  cited_brands: { name: string }[];
}

export interface BrandMetrics {
  n_runs: number;
  sov: number;
  citation_rate: number;
  avg_position: number | null;
}

/**
 * Probabilistic metrics over N runs (spec §6). Returns zeros (never NaN) for an
 * empty set so the dashboard renders "ยังไม่ถูกอ้างอิง" instead of erroring.
 */
export function computeBrandMetrics(runs: RunFacts[]): BrandMetrics {
  const n = runs.length;
  if (n === 0) return { n_runs: 0, sov: 0, citation_rate: 0, avg_position: null };

  const mentioned = runs.filter((r) => r.brand_mentioned).length;
  const urlCited = runs.filter((r) => r.brand_url_cited).length;
  const positions = runs
    .map((r) => r.brand_position)
    .filter((p): p is number => typeof p === "number" && p > 0);

  return {
    n_runs: n,
    sov: mentioned / n,
    citation_rate: urlCited / n,
    avg_position: positions.length ? positions.reduce((a, b) => a + b, 0) / positions.length : null,
  };
}

/** Per-competitor SoV, matching by canonical name OR any Thai/English alias. */
export function computeCompetitorSov(
  competitors: Competitor[],
  runs: RunFacts[],
): Record<string, number> {
  const out: Record<string, number> = {};
  const n = runs.length;
  if (n === 0) {
    for (const c of competitors) out[c.name] = 0;
    return out;
  }
  for (const comp of competitors) {
    const needles = [comp.name, ...(comp.aliases ?? [])].map((s) => s.toLowerCase());
    let hits = 0;
    for (const r of runs) {
      if (r.cited_brands.some((c) => needles.includes((c.name ?? "").toLowerCase()))) hits++;
    }
    out[comp.name] = hits / n;
  }
  return out;
}
