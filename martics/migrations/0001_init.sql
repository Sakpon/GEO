-- martics GEO Citation Tracker — initial schema (Phases 0–2).
-- Mirrors build-spec §8. `runs.status`/`runs.error` added so a failed engine
-- call is recorded and retried next cycle without collapsing the whole cycle.

CREATE TABLE IF NOT EXISTS clients (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  logo_url   TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS brands (
  id               TEXT PRIMARY KEY,
  client_id        TEXT NOT NULL REFERENCES clients(id),
  name             TEXT NOT NULL,
  domain           TEXT NOT NULL,
  aliases_json     TEXT NOT NULL DEFAULT '[]',   -- ["the dent","เดอะ เดนท์"]
  competitors_json TEXT NOT NULL DEFAULT '[]',   -- [{name,domain,aliases:[]}]
  created_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_brands_client ON brands(client_id);

CREATE TABLE IF NOT EXISTS prompts (
  id         TEXT PRIMARY KEY,
  brand_id   TEXT NOT NULL REFERENCES brands(id),
  text_th    TEXT NOT NULL,
  intent     TEXT NOT NULL DEFAULT 'informational', -- informational|local|commercial
  active     INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prompts_brand ON prompts(brand_id);

CREATE TABLE IF NOT EXISTS runs (
  id               TEXT PRIMARY KEY,
  prompt_id        TEXT NOT NULL REFERENCES prompts(id),
  engine           TEXT NOT NULL,
  run_index        INTEGER NOT NULL,
  status           TEXT NOT NULL DEFAULT 'ok',     -- ok|failed
  error            TEXT,
  raw_response     TEXT,
  brand_mentioned  INTEGER NOT NULL DEFAULT 0,
  brand_url_cited  INTEGER NOT NULL DEFAULT 0,
  brand_position   INTEGER,                          -- 1 = first mentioned; NULL if absent
  cited_brands_json TEXT NOT NULL DEFAULT '[]',      -- [{name,position}]
  cited_urls_json  TEXT NOT NULL DEFAULT '[]',       -- [{url,domain,owner}]
  run_at           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_prompt_engine ON runs(prompt_id, engine, run_at);

CREATE TABLE IF NOT EXISTS metrics_daily (
  id                  TEXT PRIMARY KEY,
  brand_id            TEXT NOT NULL REFERENCES brands(id),
  prompt_id           TEXT NOT NULL REFERENCES prompts(id),
  engine              TEXT NOT NULL,
  date                TEXT NOT NULL,                 -- YYYY-MM-DD (UTC)
  n_runs              INTEGER NOT NULL,
  sov                 REAL NOT NULL,
  citation_rate       REAL NOT NULL,
  avg_position        REAL,
  competitor_sov_json TEXT NOT NULL DEFAULT '{}',    -- {competitorName: sov}
  UNIQUE (brand_id, prompt_id, engine, date)
);
CREATE INDEX IF NOT EXISTS idx_metrics_brand_date ON metrics_daily(brand_id, date);

CREATE TABLE IF NOT EXISTS fixes (
  id                   TEXT PRIMARY KEY,
  brand_id             TEXT NOT NULL REFERENCES brands(id),
  prompt_id            TEXT NOT NULL REFERENCES prompts(id),
  gap_summary          TEXT,
  recommendations_json TEXT NOT NULL DEFAULT '[]',
  source_urls_json     TEXT NOT NULL DEFAULT '[]',
  created_at           TEXT NOT NULL
);
