import type { DashboardPayload } from "../api";

const pct = (n: number) => `${Math.round(n * 100)}%`;

export function CompetitorTable({ data }: { data: DashboardPayload }) {
  const brandSov = data.summary.sov;
  const rows = [
    { name: `${data.brand.name} (เรา)`, sov: brandSov, self: true },
    ...data.competitors.map((c) => ({ ...c, self: false })),
  ].sort((a, b) => b.sov - a.sov);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">แบรนด์ที่ AI พูดถึง (วันล่าสุด)</h2>
      {rows.length === 1 && data.competitors.length === 0 ? (
        <p className="py-6 text-center text-sm text-slate-400">ยังไม่มีคู่แข่งในข้อมูล</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase text-slate-400">
              <th className="pb-2">แบรนด์</th>
              <th className="pb-2 text-right">SoV</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name} className={r.self ? "font-semibold text-brand" : ""}>
                <td className="border-t border-slate-100 py-2">{r.name}</td>
                <td className="border-t border-slate-100 py-2 text-right">{pct(r.sov)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
