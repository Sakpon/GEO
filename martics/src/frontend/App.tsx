import { useCallback, useEffect, useState } from "react";
import {
  apiDashboard,
  apiGetBrands,
  apiRun,
  type BrandRow,
  type DashboardPayload,
} from "./api";
import { MetricCards } from "./components/MetricCards";
import { TimeSeriesChart } from "./components/TimeSeriesChart";
import { CompetitorTable } from "./components/CompetitorTable";
import { PromptTable } from "./components/PromptTable";
import { NewBrandForm } from "./components/NewBrandForm";

export default function App() {
  const [brands, setBrands] = useState<BrandRow[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const loadBrands = useCallback(async () => {
    const { brands } = await apiGetBrands();
    setBrands(brands);
    if (brands.length && !selected) setSelected(brands[0].id);
    if (brands.length === 0) setShowForm(true);
  }, [selected]);

  const loadDashboard = useCallback(async (brandId: string) => {
    setDashboard(await apiDashboard(brandId));
  }, []);

  useEffect(() => {
    loadBrands().catch((e) => setMsg((e as Error).message));
  }, [loadBrands]);

  useEffect(() => {
    if (selected) loadDashboard(selected).catch((e) => setMsg((e as Error).message));
  }, [selected, loadDashboard]);

  async function run() {
    if (!selected) return;
    setRunning(true);
    setMsg(null);
    try {
      const res = await apiRun(selected);
      const ok = res.runs.reduce((a, r) => a + r.ok, 0);
      const failed = res.runs.reduce((a, r) => a + r.failed, 0);
      setMsg(`รันเสร็จ: ${ok} runs สำเร็จ, ${failed} ล้มเหลว, เขียน ${res.metrics_written} metric`);
      await loadDashboard(selected);
    } catch (e) {
      setMsg((e as Error).message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            martics <span className="text-brand">· GEO Citation Tracker</span>
          </h1>
          <p className="text-sm text-slate-500">AI Share-of-Voice ภาษาไทย · MVP (Perplexity scaffold)</p>
        </div>
      </header>

      <div className="mb-5 flex flex-wrap items-center gap-3">
        <select
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {brands.length === 0 && <option value="">— ยังไม่มีแบรนด์ —</option>}
          {brands.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name} ({b.domain})
            </option>
          ))}
        </select>
        <button
          onClick={run}
          disabled={!selected || running}
          className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50"
        >
          {running ? "กำลังรัน…" : "▶ Run now"}
        </button>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          {showForm ? "ปิดฟอร์ม" : "+ เพิ่มแบรนด์"}
        </button>
      </div>

      {msg && <p className="mb-4 rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-600">{msg}</p>}

      {showForm && (
        <div className="mb-6">
          <NewBrandForm
            onCreated={async (id) => {
              setShowForm(false);
              await loadBrands();
              setSelected(id);
            }}
          />
        </div>
      )}

      {dashboard && (
        <div className="space-y-5">
          <MetricCards data={dashboard} />
          <TimeSeriesChart data={dashboard} />
          <div className="grid gap-5 md:grid-cols-2">
            <CompetitorTable data={dashboard} />
            <PromptTable data={dashboard} />
          </div>
        </div>
      )}
    </div>
  );
}
