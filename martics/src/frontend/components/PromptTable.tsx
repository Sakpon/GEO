import type { DashboardPayload } from "../api";

const pct = (n: number) => `${Math.round(n * 100)}%`;

export function PromptTable({ data }: { data: DashboardPayload }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">แยกตาม Prompt (วันล่าสุด)</h2>
      {data.prompts.length === 0 ? (
        <p className="py-6 text-center text-sm text-slate-400">ยังไม่มีข้อมูล prompt</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase text-slate-400">
              <th className="pb-2">Prompt</th>
              <th className="pb-2">Intent</th>
              <th className="pb-2 text-right">SoV</th>
              <th className="pb-2 text-right">Citation</th>
              <th className="pb-2 text-right">Pos</th>
            </tr>
          </thead>
          <tbody>
            {data.prompts.map((p) => (
              <tr key={p.prompt_id} className="align-top">
                <td className="max-w-md border-t border-slate-100 py-2 pr-3">{p.text_th}</td>
                <td className="border-t border-slate-100 py-2 text-slate-500">{p.intent}</td>
                <td className="border-t border-slate-100 py-2 text-right">{pct(p.sov)}</td>
                <td className="border-t border-slate-100 py-2 text-right">{pct(p.citation_rate)}</td>
                <td className="border-t border-slate-100 py-2 text-right">
                  {p.avg_position != null ? p.avg_position.toFixed(1) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
