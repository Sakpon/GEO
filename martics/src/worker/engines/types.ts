import type { Env } from "../types";

export interface EngineResult {
  ok: boolean;
  /** Raw, human-readable response text (answer + any cited sources appended). */
  raw: string;
  error?: string;
}

export interface Engine {
  /** Stable key stored in runs.engine / metrics_daily.engine. */
  name: string;
  query(promptText: string, env: Env): Promise<EngineResult>;
}
