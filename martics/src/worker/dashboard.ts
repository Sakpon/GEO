import type { Brand, Env } from "./types";
import { safeJSON } from "./util";

interface MetricRow {
  prompt_id: string;
  text_th: string;
  intent: string;
  engine: string;
  date: string;
  n_runs: number;
  sov: number;
  citation_rate: number;
  avg_position: number | null;
  competitor_sov_json: string;
}

export interface DashboardPayload {
  brand: { id: string; name: string; domain: string };
  has_data: boolean;
  latest_date: string | null;
  engines: string[];
  summary: {
    sov: number;
    citation_rate: number;
    avg_position: number | null;
    n_runs: number;
    cited: boolean;
    note?: string;
  };
  timeseries: { date: string; sov: number; citation_rate: number; avg_position: number | null }[];
  competitors: { name: string; sov: number }[];
  prompts: {
    prompt_id: string;
    text_th: string;
    intent: string;
    sov: number;
    citation_rate: number;
    avg_position: number | null;
  }[];
}

const mean = (xs: number[]): number => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
const meanOrNull = (xs: number[]): number | null => (xs.length ? mean(xs) : null);

export async function buildDashboard(env: Env, brand: Brand): Promise<DashboardPayload> {
  const { results } = await env.DB.prepare(
    `SELECT m.prompt_id, p.text_th, p.intent, m.engine, m.date, m.n_runs,
            m.sov, m.citation_rate, m.avg_position, m.competitor_sov_json
       FROM metrics_daily m
       JOIN prompts p ON p.id = m.prompt_id
      WHERE m.brand_id = ?
      ORDER BY m.date`,
  )
    .bind(brand.id)
    .all<MetricRow>();

  const rows = results ?? [];
  const base = { id: brand.id, name: brand.name, domain: brand.domain };

  if (rows.length === 0) {
    return {
      brand: base,
      has_data: false,
      latest_date: null,
      engines: [],
      summary: { sov: 0, citation_rate: 0, avg_position: null, n_runs: 0, cited: false, note: "ยังไม่มีข้อมูล — กด Run เพื่อเริ่มเก็บ" },
      timeseries: [],
      competitors: [],
      prompts: [],
    };
  }

  const engines = [...new Set(rows.map((r) => r.engine))].sort();

  // Time-series: average across all prompts+engines per date.
  const byDate = new Map<string, MetricRow[]>();
  for (const r of rows) (byDate.get(r.date) ?? byDate.set(r.date, []).get(r.date)!).push(r);
  const timeseries = [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, rs]) => ({
      date,
      sov: mean(rs.map((r) => r.sov)),
      citation_rate: mean(rs.map((r) => r.citation_rate)),
      avg_position: meanOrNull(rs.map((r) => r.avg_position).filter((p): p is number => p != null)),
    }));

  const latestDate = timeseries[timeseries.length - 1].date;
  const latestRows = byDate.get(latestDate)!;

  const summarySov = mean(latestRows.map((r) => r.sov));
  const summaryCitation = mean(latestRows.map((r) => r.citation_rate));
  const summary = {
    sov: summarySov,
    citation_rate: summaryCitation,
    avg_position: meanOrNull(latestRows.map((r) => r.avg_position).filter((p): p is number => p != null)),
    n_runs: latestRows.reduce((a, r) => a + r.n_runs, 0),
    cited: summarySov > 0 || summaryCitation > 0,
    note: summarySov > 0 || summaryCitation > 0 ? undefined : "ยังไม่ถูกอ้างอิง",
  };

  // Competitor leaderboard from the latest day (averaged across prompts/engines).
  const compTotals = new Map<string, number[]>();
  for (const r of latestRows) {
    const csov = safeJSON<Record<string, number>>(r.competitor_sov_json, {});
    for (const [name, v] of Object.entries(csov)) {
      (compTotals.get(name) ?? compTotals.set(name, []).get(name)!).push(v);
    }
  }
  const competitors = [...compTotals.entries()]
    .map(([name, vs]) => ({ name, sov: mean(vs) }))
    .sort((a, b) => b.sov - a.sov);

  // Per-prompt breakdown (latest day, averaged across engines).
  const byPrompt = new Map<string, MetricRow[]>();
  for (const r of latestRows) (byPrompt.get(r.prompt_id) ?? byPrompt.set(r.prompt_id, []).get(r.prompt_id)!).push(r);
  const prompts = [...byPrompt.values()].map((rs) => ({
    prompt_id: rs[0].prompt_id,
    text_th: rs[0].text_th,
    intent: rs[0].intent,
    sov: mean(rs.map((r) => r.sov)),
    citation_rate: mean(rs.map((r) => r.citation_rate)),
    avg_position: meanOrNull(rs.map((r) => r.avg_position).filter((p): p is number => p != null)),
  }));

  return {
    brand: base,
    has_data: true,
    latest_date: latestDate,
    engines,
    summary,
    timeseries,
    competitors,
    prompts,
  };
}
