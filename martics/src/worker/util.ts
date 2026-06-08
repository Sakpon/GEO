/** UTC date string YYYY-MM-DD — the bucket key for metrics_daily. */
export function todayUTC(d: Date = new Date()): string {
  return d.toISOString().slice(0, 10);
}

export function nowISO(): string {
  return new Date().toISOString();
}

export function newId(): string {
  return crypto.randomUUID();
}

/** Best-effort domain extraction; returns "" for un-parseable URLs. */
export function domainOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

export function safeJSON<T>(raw: string | null | undefined, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}
