import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DashboardPayload } from "../api";

export function TimeSeriesChart({ data }: { data: DashboardPayload }) {
  const series = data.timeseries.map((d) => ({
    date: d.date.slice(5), // MM-DD
    sov: Math.round(d.sov * 100),
    citation: Math.round(d.citation_rate * 100),
  }));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">เทรนด์ SoV &amp; Citation (รายวัน)</h2>
      {series.length === 0 ? (
        <p className="py-12 text-center text-sm text-slate-400">ยังไม่มีข้อมูลเทรนด์</p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={series} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} unit="%" tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v: number) => `${v}%`} />
            <Line type="monotone" dataKey="sov" name="SoV" stroke="#0f766e" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="citation" name="Citation" stroke="#d97706" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
