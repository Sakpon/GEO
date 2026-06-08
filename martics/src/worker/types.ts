export interface Env {
  // Bindings
  DB: D1Database;
  CONFIG: KVNamespace;
  ASSETS: Fetcher;

  // Vars (wrangler.toml [vars])
  RUNS_PER_CYCLE: string;
  ACTIVE_ENGINES: string;
  PARSER_MODEL: string;

  // Secrets (wrangler secret put)
  ANTHROPIC_API_KEY: string;
  PERPLEXITY_API_KEY?: string;
  GEMINI_API_KEY?: string;
}

export interface Competitor {
  name: string;
  domain?: string;
  aliases?: string[];
}

export interface Brand {
  id: string;
  client_id: string;
  name: string;
  domain: string;
  aliases: string[];
  competitors: Competitor[];
  created_at: string;
}

export interface Prompt {
  id: string;
  brand_id: string;
  text_th: string;
  intent: string;
  active: number;
  created_at: string;
}

/** Result of parsing one raw engine response (parser contract, spec §9). */
export interface ParseResult {
  brand_mentioned: boolean;
  brand_url_cited: boolean;
  brand_position: number | null;
  cited_brands: { name: string; position: number }[];
  cited_urls: { url: string; domain: string; owner: "brand" | "competitor" | "other" }[];
}

export const runsPerCycle = (env: Env): number => {
  const n = parseInt(env.RUNS_PER_CYCLE ?? "5", 10);
  return Number.isFinite(n) && n > 0 ? n : 5;
};

export const activeEngines = (env: Env): string[] =>
  (env.ACTIVE_ENGINES ?? "perplexity")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
