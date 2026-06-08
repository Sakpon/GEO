import { useState } from "react";
import { apiAddPrompts, apiCreateBrand } from "../api";

export function NewBrandForm({ onCreated }: { onCreated: (brandId: string) => void }) {
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [aliases, setAliases] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [prompts, setPrompts] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const competitorList = competitors
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
        .map((line) => {
          const [cname, cdomain, ...cal] = line.split(",").map((s) => s.trim());
          return { name: cname, domain: cdomain || undefined, aliases: cal.filter(Boolean) };
        });

      const brand = await apiCreateBrand({
        name,
        domain,
        aliases: aliases.split(",").map((s) => s.trim()).filter(Boolean),
        competitors: competitorList,
      });

      const promptList = prompts
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean)
        .map((text_th) => ({ text_th, intent: "informational" }));
      if (promptList.length) await apiAddPrompts(brand.id, promptList);

      onCreated(brand.id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const field = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand focus:outline-none";

  return (
    <form onSubmit={submit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-slate-800">เพิ่มแบรนด์ใหม่</h2>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="block text-sm">
          ชื่อแบรนด์
          <input className={field} value={name} onChange={(e) => setName(e.target.value)} required placeholder="The Dent" />
        </label>
        <label className="block text-sm">
          โดเมน
          <input className={field} value={domain} onChange={(e) => setDomain(e.target.value)} required placeholder="thedent.co.th" />
        </label>
      </div>
      <label className="block text-sm">
        Aliases (คั่นด้วย ,)
        <input className={field} value={aliases} onChange={(e) => setAliases(e.target.value)} placeholder="the dent, เดอะ เดนท์" />
      </label>
      <label className="block text-sm">
        คู่แข่ง — บรรทัดละราย: ชื่อ, โดเมน, alias…
        <textarea className={field} rows={3} value={competitors} onChange={(e) => setCompetitors(e.target.value)} placeholder="BIDC, bangkokdental.com&#10;Thantakit, thantakit.com" />
      </label>
      <label className="block text-sm">
        Prompts ภาษาไทย — บรรทัดละ prompt
        <textarea className={field} rows={4} value={prompts} onChange={(e) => setPrompts(e.target.value)} placeholder="ทำรากฟันเทียมที่ไหนดี กรุงเทพ&#10;จัดฟันใสคลินิกไหนดี" />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50"
      >
        {busy ? "กำลังสร้าง…" : "สร้างแบรนด์"}
      </button>
    </form>
  );
}
