export interface BrandRow {
  id: string;
  name: string;
  domain: string;
  client_id: string;
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

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data as { error?: string }).error || `HTTP ${res.status}`);
  return data as T;
}

export const apiGetBrands = () => req<{ brands: BrandRow[] }>("/brands");

export const apiCreateBrand = (body: {
  name: string;
  domain: string;
  aliases: string[];
  competitors: { name: string; domain?: string; aliases?: string[] }[];
}) => req<BrandRow>("/brands", { method: "POST", body: JSON.stringify(body) });

export const apiAddPrompts = (brand_id: string, prompts: { text_th: string; intent: string }[]) =>
  req<{ count: number }>("/prompts", {
    method: "POST",
    body: JSON.stringify({ brand_id, prompts }),
  });

export const apiRun = (brand_id: string) =>
  req<{ metrics_written: number; runs: { ok: number; failed: number }[] }>("/run", {
    method: "POST",
    body: JSON.stringify({ brand_id }),
  });

export const apiDashboard = (brand_id: string) =>
  req<DashboardPayload>(`/dashboard?brand_id=${encodeURIComponent(brand_id)}`);
