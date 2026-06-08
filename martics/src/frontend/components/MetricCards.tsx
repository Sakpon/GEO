import type { DashboardPayload } from "../api";

const pct = (n: number) => `${Math.round(n * 100)}%`;

function Card({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-3xl font-semibold text-slate-900">{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-400">{sub}</div>}
    </div>
  );
}

export function MetricCards({ data }: { data: DashboardPayload }) {
  const s = data.summary;
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <Card label="Share of Voice" value={pct(s.sov)} sub={s.note} />
      <Card label="Citation Rate" value={pct(s.citation_rate)} sub="URL ของแบรนด์ถูกอ้าง" />
      <Card
        label="Avg Position"
        value={s.avg_position != null ? s.avg_position.toFixed(1) : "—"}
        sub="1 = ถูกพูดถึงก่อน"
      />
      <Card label="Runs (ล่าสุด)" value={String(s.n_runs)} sub={data.latest_date ?? ""} />
    </div>
  );
}
